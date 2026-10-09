from app.core.supabase import create_db_client


TENANT_ID = "fc923830-3178-4cf8-98b2-23c2bc4e0015"

db = create_db_client()


response = (
    db
    .table("document_chunks")
    .select(
        """
        id,
        tenant_id,
        embedding
        """
    )
    .eq("tenant_id", TENANT_ID)
    .limit(10)
    .execute()
)


print("CHUNKS FOUND:", len(response.data))

for chunk in response.data:
    embedding = chunk["embedding"]

    print()
    print("ID:", chunk["id"])
    print("EMBEDDING TYPE:", type(embedding))
    print("EMBEDDING EXISTS:", embedding is not None)

    if embedding is not None:
        print("EMBEDDING LENGTH:", len(embedding))
