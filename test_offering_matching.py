from app.core.supabase import create_db_client
from app.services.offerings import find_offering_from_query


TENANT_ID = "fc923830-3178-4cf8-98b2-23c2bc4e0015"

db = create_db_client()


queries = [
    "How much is the AI Business Assistant?",
    "How much is consultation?",
    "What does your consultation cost?",
    "How much do you charge for AI consulting?",
    "Tell me about your consulting service.",
    "Is consultation available?",
    "How many AI Business Assistants do you have?",
]


for query in queries:
    result = find_offering_from_query(
        query=query,
        tenant_id=TENANT_ID,
        db=db,
    )

    print()
    print("QUERY:", query)
    print("RESULT:", result)
