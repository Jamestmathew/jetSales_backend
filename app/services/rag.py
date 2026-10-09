from supabase import Client

from app.services.embeddings import generate_embeddings


def search_documents(
    query: str,
    tenant_id: str,
    db: Client,
    limit: int = 5,
):
    """
    Search the tenant's document chunks using
    semantic similarity.

    Returns:
        List of matching document chunks.
    """

    query_embedding = generate_embeddings(
        [query],
        input_type="search_query",
    )[0]

    response = db.rpc(
        "match_document_chunks",
        {
            "query_embedding": query_embedding,
            "match_tenant_id": tenant_id,
            "match_threshold": 0.3,
            "match_count": limit,
        },
    ).execute()

    return response.data

