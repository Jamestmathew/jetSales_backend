from app.core.supabase import create_db_client
from app.services.rag import search_documents


TENANT_ID = "fc923830-3178-4cf8-98b2-23c2bc4e0015"

db = create_db_client()


questions = [
    "What is your refund policy?",
    "How does your service work?",
    "What is the AI Business Assistant?",
]


for question in questions:

    print()
    print("=" * 60)
    print("QUESTION:", question)

    results = search_documents(
        query=question,
        tenant_id=TENANT_ID,
        db=db,
    )

    print("RESULTS FOUND:", len(results))

    for result in results:
        print()
        print("SIMILARITY:", result["similarity"])
        print("CONTENT:", result["content"])

