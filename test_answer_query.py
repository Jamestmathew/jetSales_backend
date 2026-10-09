from app.core.supabase import create_db_client
from app.services.answer_query import answer_query


TENANT_ID = "fc923830-3178-4cf8-98b2-23c2bc4e0015"

db = create_db_client()


questions = [
    "How much is the AI Business Assistant?",
    "Is the AI Business Assistant available?",
    "How many AI Business Assistants do you have?",
    "What kind of technology solutions does JetIntel Technologies provide?",
    "What is your refund policy?",
    "Tell me about the AI Business Assistant and how much does it cost?",
]



for question in questions:

    print()
    print("=" * 60)
    print("QUESTION:", question)
    print("=" * 60)

    answer = answer_query(
        question=question,
        tenant_id=TENANT_ID,
        db=db,
    )

    print("ANSWER:")
    print(answer)
