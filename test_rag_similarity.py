from app.core.supabase import create_db_client
from app.services.embeddings import generate_embeddings


TENANT_ID = "fc923830-3178-4cf8-98b2-23c2bc4e0015"

db = create_db_client()


question = "What kind of technology solutions does JetIntel Technologies provide?"

query_embedding = generate_embeddings(
    [question],
    input_type="search_query",
)[0]


print("QUERY:", question)
print("EMBEDDING LENGTH:", len(query_embedding))


response = db.rpc(
    "match_document_chunks",
    {
        "query_embedding": query_embedding,
        "match_tenant_id": TENANT_ID,
        "match_threshold": 0.0,
        "match_count": 5,
    },
).execute()


print()
print("RESULTS FOUND:", len(response.data))


for result in response.data:
    print()
    print("SIMILARITY:", result["similarity"])
    print("CONTENT:", result["content"])
