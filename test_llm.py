
from app.services.llm import generate_answer

context = """
STRUCTURED OFFERING DATA:
Name: AI Business Assistant
Type: product
Description: AI-powered website assistant for answering customer
questions and capturing leads.
Price: 150000 NGN
Available: True
Quantity: 10
SKU: JET-AI-001

BUSINESS KNOWLEDGE:
The AI Business Assistant is a website-based assistant designed
to help businesses answer customer questions and capture leads.
"""

question = "Tell me about the AI Business Assistant and its price."

try:
    answer = generate_answer(
        question=question,
        context=context,
    )

    print("GROQ ANSWER:")
    print(answer)

except Exception as error:
    print("LLM TEST FAILED")
    print("Error type:", type(error).__name__)
    print("Error message:", str(error))