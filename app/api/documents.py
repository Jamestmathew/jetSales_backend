from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from requests import request

from app.core.security import (
    get_current_tenant,
    require_owner,
    get_db,
)

from app.services.embeddings import generate_embeddings
from app.services.chunking import chunk_text
from app.services.pdf import extract_text_from_pdf
from app.services.cleaning import clean_text
from app.services.rag import search_documents
from app.services.answer_query import answer_query

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


# ============================================
# REQUEST MODELS
# ============================================

class ChatRequest(BaseModel):
    message: str


class DocumentIngestRequest(BaseModel):
    name: str
    content: str


# ============================================
# INGEST TEXT DOCUMENT
# ============================================

@router.post("/ingest")
def ingest_document(
    request: DocumentIngestRequest,
    tenant=Depends(get_current_tenant),
    db=Depends(get_db),
):
    tenant_id = tenant["tenant_id"]

    # 1. Split document into chunks
    chunks = chunk_text(
        request.content,
        chunk_size=1000,
        chunk_overlap=200
    )

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="Could not create document chunks"
        )

    # 2. Create document record
    document_response = (
        db
        .table("documents")
        .insert({
            "tenant_id": tenant_id,
            "name": request.name,
        })
        .execute()
    )

    if not document_response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to create document"
        )

    document = document_response.data[0]
    document_id = document["id"]

    # 3. Generate embeddings
    embeddings = generate_embeddings(
        chunks,
        input_type="search_document"
    )

    if len(embeddings) != len(chunks):
        raise HTTPException(
            status_code=500,
            detail="Number of embeddings does not match chunks"
        )

    # 4. Prepare chunk records
    chunk_rows = []

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        chunk_rows.append({
            "document_id": document_id,
            "tenant_id": tenant_id,
            "content": chunk,
            "embedding": embedding,
            "chunk_index": index,
        })

    # 5. Store chunks
    chunk_response = (
        db
        .table("document_chunks")
        .insert(chunk_rows)
        .execute()
    )

    if not chunk_response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to store document chunks"
        )

    return {
        "message": "Document ingested successfully",
        "document_id": document_id,
        "tenant_id": tenant_id,
        "chunks_created": len(chunks),
        "chunks_embedded": len(embeddings),
    }


# ============================================
# UPLOAD PDF
# ============================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    tenant=Depends(get_current_tenant),
    db=Depends(get_db),
):
    """
    Upload a PDF document and add it to the
    authenticated user's tenant knowledge base.
    """

    tenant_id = tenant["tenant_id"]

    # 1. Make sure uploaded file is PDF
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # 2. Save uploaded PDF temporarily
    import tempfile
    import os

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp_file:
        temp_file.write(file_bytes)
        temp_file_path = temp_file.name

    try:
        # 3. Extract text
        raw_text = extract_text_from_pdf(
            temp_file_path
        )

        # 4. Clean text
        cleaned_text = clean_text(
            raw_text
        )

        if not cleaned_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in PDF"
            )

        # 5. Create chunks
        chunks = chunk_text(
            cleaned_text,
            chunk_size=1000,
            chunk_overlap=200
        )

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Could not create document chunks"
            )

        # 6. Create document record
        document_response = (
            db
            .table("documents")
            .insert({
                "tenant_id": tenant_id,
                "name": file.filename,
                "file_type": "application/pdf",
            })
            .execute()
        )

        if not document_response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create document"
            )

        document = document_response.data[0]
        document_id = document["id"]

        # 7. Generate embeddings
        embeddings = generate_embeddings(
            chunks,
            input_type="search_document"
        )

        if len(embeddings) != len(chunks):
            raise HTTPException(
                status_code=500,
                detail="Number of embeddings does not match chunks"
            )

        # 8. Prepare chunk records
        chunk_rows = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            chunk_rows.append({
                "document_id": document_id,
                "tenant_id": tenant_id,
                "content": chunk,
                "embedding": embedding,
                "chunk_index": index,
            })

        # 9. Store chunks
        chunk_response = (
            db
            .table("document_chunks")
            .insert(chunk_rows)
            .execute()
        )

        if not chunk_response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to store document chunks"
            )

        return {
            "message": "PDF uploaded and ingested successfully",
            "document_id": document_id,
            "tenant_id": tenant_id,
            "filename": file.filename,
            "chunks_created": len(chunks),
            "chunks_embedded": len(embeddings),
        }

    finally:
        # 10. Delete temporary PDF
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


# ============================================
# EMBED EXISTING DOCUMENT
# ============================================

@router.post("/{document_id}/embed")
def embed_document(
    document_id: str,
    tenant=Depends(get_current_tenant),
    db=Depends(get_db),
):
    tenant_id = tenant["tenant_id"]

    # 1. Get document belonging to current tenant
    document_response = (
        db
        .table("documents")
        .select("*")
        .eq("id", document_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )

    if not document_response.data:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # 2. Get chunks belonging to this document
    chunks_response = (
        db
        .table("document_chunks")
        .select("*")
        .eq("document_id", document_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )

    chunks = chunks_response.data

    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No chunks found for this document"
        )

    # 3. Get chunk content
    texts = [
        chunk["content"]
        for chunk in chunks
    ]

    # 4. Generate embeddings
    embeddings = generate_embeddings(
        texts,
        input_type="search_document"
    )

    if len(embeddings) != len(chunks):
        raise HTTPException(
            status_code=500,
            detail="Number of embeddings does not match chunks"
        )

    # 5. Update each chunk
    for chunk, embedding in zip(
        chunks,
        embeddings
    ):
        (
            db
            .table("document_chunks")
            .update({
                "embedding": embedding
            })
            .eq("id", chunk["id"])
            .eq("tenant_id", tenant_id)
            .execute()
        )

    return {
        "message": "Document embeddings generated successfully",
        "document_id": document_id,
        "tenant_id": tenant_id,
        "chunks_embedded": len(embeddings),
    }


# ============================================
# SEARCH DOCUMENTS
# ============================================

@router.get("/search")
def search(
    query: str,
    tenant=Depends(get_current_tenant),
    db=Depends(get_db),
):
    tenant_id = tenant["tenant_id"]

    results = search_documents(
        query=query,
        tenant_id=tenant_id,
        db=db,
    )

    return {
        "query": query,
        "tenant_id": tenant_id,
        "results": results,
    }


# ============================================
# CHAT WITH DOCUMENTS
# ============================================

@router.post("/chat")
def chat(
    request: ChatRequest,
    tenant=Depends(get_current_tenant),
    db=Depends(get_db),
):
    tenant_id = tenant["tenant_id"]

    result = answer_query(
        question=request.message,
        tenant_id=tenant_id,
        db=db,
)

    return {
        "message": request.message,
         "tenant_id": tenant_id,
         "answer": result["answer"],
         "products": result["products"],
}

# ============================================
# DELETE DOCUMENT
# ============================================

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    tenant=Depends(require_owner),
    db=Depends(get_db),
):
    tenant_id = tenant["tenant_id"]

    # 1. Find document belonging to current tenant
    document_response = (
        db
        .table("documents")
        .select("id")
        .eq("id", document_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )

    if not document_response.data:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # 2. Delete document
    delete_response = (
        db
        .table("documents")
        .delete()
        .eq("id", document_id)
        .eq("tenant_id", tenant_id)
        .execute()
    )

    if not delete_response.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete document"
        )

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
        "tenant_id": tenant_id,
    }
