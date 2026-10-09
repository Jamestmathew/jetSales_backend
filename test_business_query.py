from app.core.supabase import create_db_client
from app.services.business_query import search_business_data


TENANT_ID = "fc923830-3178-4cf8-98b2-23c2bc4e0015"

db = create_db_client()

queries = [
    "How many products do you have?",
    "What products do you have?",
    "How many AI Business Assistants do you have?",
    "How much is the AI Business Assistant?",
    "Is the AI Business Assistant available?",
    "Tell me about the AI Business Assistant?",
    "How much is the AI Consultation?",
    "Is the AI Consultation available?",
    "Tell me about the AI Consultation?",
]


for query in queries:
    print("\n" + "=" * 60)
    print("QUESTION:", query)
    print("=" * 60)

    result = search_business_data(
        query=query,
        tenant_id=TENANT_ID,
        db=db,
    )

    print(result)
