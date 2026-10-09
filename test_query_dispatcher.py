
from app.core.supabase import create_db_client
from app.services.query_dispatcher import dispatch_query


TENANT_ID = "fc923830-3178-4cf8-98b2-23c2bc4e0015"

db = create_db_client()


queries = [
    "How much is the AI Business Assistant?",
    "How many AI Business Assistants do you have?",
    "Is the AI Business Assistant available?",
    "What products do you have?",
    "What is your refund policy?",
    "How does your service work?",
    "Tell me about the AI Business Assistant and how much does it cost?",
]


for query in queries:

    print()
    print("=" * 60)
    print("QUESTION:", query)

    result = dispatch_query(
        query=query,
        tenant_id=TENANT_ID,
        db=db,
    )

    print("RESULT:", result)
