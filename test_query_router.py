from app.services.query_router import route_query


questions = [
    "How much is the AI Business Assistant?",
    "How many AI Business Assistants do you have?",
    "Is the AI Business Assistant available?",
    "What products do you have?",
    "What is your refund policy?",
    "How does your service work?",
    "Tell me about your business.",
    "Tell me about the AI Business Assistant and how much does it cost?",
]


for question in questions:

    print()
    print("=" * 60)
    print("QUESTION:", question)
    print("RESULT:", route_query(question))
