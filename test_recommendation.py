from app.core.supabase import create_db_client

from app.services.offerings import get_recommendation_candidates


TENANT_ID = "fc923830-3178-4cf8-98b2-23c2bc4e0015"


db = create_db_client()

candidates = get_recommendation_candidates(
    tenant_id=TENANT_ID,
    db=db,
)


queries = [
    "I need something that can answer customer questions on my website and capture leads.",
    "I want an AI assistant for my website that can talk to visitors and collect their information.",
    "How can I automatically answer questions from people visiting my website?",
    "I need a tool that can help me turn website visitors into leads.",
    "Can you recommend something for handling customer questions on my website?",
    "I want to stop losing potential customers because nobody responds to their questions.",
    "I need something that can engage website visitors and help me collect their contact details.",
]


print("\nCANDIDATES:")

for candidate in candidates:
    print("\n---")
    print("Name:", candidate["name"])
    print("Description:", candidate["description"])
    print("Aliases:", candidate["aliases"])


print("\n\nRECOMMENDATION QUERIES:")

for query in queries:
    print("\n---")
    print(query)
