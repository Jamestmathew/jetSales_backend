
from app.services.business_query import detect_business_intent


STRUCTURED_INTENTS = [
    "price",
    "quantity",
    "availability",
    "product_list",
    "recommendation",
]


COMPANY_INFORMATION_PHRASES = [
    "what do you do",
    "what does your company do",
    "what does your business do",
    "what does this company do",
    "what does this business do",
    "tell me about your company",
    "tell me about your business",
    "tell me about this company",
    "tell me about this business",
    "who are you",
    "who is your company",
    "who is your business",
    "what is your company about",
    "what is your business about",
    "what kind of company are you",
    "what kind of business are you",
    "introduce your company",
    "introduce your business",
    "what services do you offer",
    "what services does your company offer",
    "what products do you offer",
    "what solutions do you provide",
    "what can you help me with",
    "what can your company help me with",
    "what are your capabilities",
]


KNOWLEDGE_INDICATORS = [
    "tell me about",
    "what is",
    "what's",
    "describe",
    "how does",
    "how do",
    "explain",
    "information about",
    "details about",
    "who is",
    "who are",
    "what are",
    "what do",
    "what does",
    "what can",
    "what kind of",
    "introduce",
]


def route_query(query: str):
    """
    Decide which information sources are required
    to answer a customer question.

    Possible routes:
    - structured
    - rag
    - hybrid

    Company-information questions are routed to RAG
    unless structured business information is also needed.
    """

    intent = detect_business_intent(query)

    query_lower = " ".join(query.lower().split())

    needs_structured = intent in STRUCTURED_INTENTS

    is_company_information_question = any(
        phrase in query_lower
        for phrase in COMPANY_INFORMATION_PHRASES
    )

    needs_rag = (
        is_company_information_question
        or any(
            phrase in query_lower
            for phrase in KNOWLEDGE_INDICATORS
        )
    )

    if needs_structured and needs_rag:
        return {
            "route": "hybrid",
            "intent": intent,
            "needs_structured": True,
            "needs_rag": True,
        }

    if needs_structured:
        return {
            "route": "structured",
            "intent": intent,
            "needs_structured": True,
            "needs_rag": False,
        }

    return {
        "route": "rag",
        "intent": "knowledge",
        "needs_structured": False,
        "needs_rag": True,
    }
