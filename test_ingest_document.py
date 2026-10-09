from app.core.supabase import create_db_client
from app.services.chunking import chunk_text
from app.services.embeddings import generate_embeddings


TENANT_ID = "fc923830-3178-4cf8-98b2-23c2bc4e0015"


content = """
The AI Business Assistant is a website-based assistant designed to help
businesses answer customer questions and capture leads.

It helps businesses provide information about their products and services
and helps customers understand available offerings.

The AI Business Assistant is designed to support businesses by handling
customer questions and helping businesses capture potential leads.
"""


db = create_db_client()


# 1. Create document
document_response = (
    db
    .table("documents")
    .insert({
        "tenant_id": TENANT_ID,
        "name": "AI Business Assistant Knowledge",
    })
    .execute()
)


document = document_response.data[0]
document_id = document["id"]


print("DOCUMENT CREATED:")
print(document_id)


# 2. Create chunks
chunks = chunk_text(
    content,
    chunk_size=1000,
    chunk_overlap=200,
)


print()
print("CHUNKS CREATED:", len(chunks))


# 3. Generate embeddings
embeddings = generate_embeddings(
    chunks,
    input_type="search_document",
)


print("EMBEDDINGS CREATED:", len(embeddings))


# 4. Prepare chunk records
chunk_rows = []

for index, (chunk, embedding) in enumerate(
    zip(chunks, embeddings)
):
    chunk_rows.append({
        "document_id": document_id,
        "tenant_id": TENANT_ID,
        "content": chunk,
        "embedding": embedding,
        "chunk_index": index,
    })


# 5. Store chunks
response = (
    db
    .table("document_chunks")
    .insert(chunk_rows)
    .execute()
)


print()
print("CHUNKS STORED:", len(response.data))
