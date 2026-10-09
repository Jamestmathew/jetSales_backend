
from app.core.security import get_db
from app.services.query_dispatcher import dispatch_query
from app.services.context_builder import build_context

tenant_id = "fc923830-3178-4cf8-98b2-23c2bc4e0015"

questions = [
    "What products do you have?",
    "Tell me about the AI Business Assistant and its price.",
    "What do you do?",
]

db = get_db()

for question in questions:
    print("\n" + "=" * 70)
    print("QUESTION:", question)

    try:
        result = dispatch_query(
            query=question,
            tenant_id=tenant_id,
            db=db,
        )

        print("ROUTE:", result["route"])

        if result["route"] == "structured":
            print("STRUCTURED RESULT:", result["data"])

            structured_result = result["data"]
            structured_data = (
                structured_result.get("data")
                if structured_result.get("found")
                else None
            )
            rag_results = None

        elif result["route"] == "hybrid":
            print("STRUCTURED RESULT:", result["structured_data"])
            print("RAG RESULTS:", result["rag_data"])

            structured_result = result["structured_data"]
            structured_data = (
                structured_result.get("data")
                if structured_result.get("found")
                else None
            )
            rag_results = result["rag_data"]

        elif result["route"] == "rag":
            print("RAG RESULTS:", result["data"])
            structured_data = None
            rag_results = result["data"]

        else:
            print("UNKNOWN ROUTE")
            structured_data = None
            rag_results = None

        context = build_context(
            structured_data=structured_data,
            rag_results=rag_results,
        )

        print("CONTEXT:", context)

    except Exception as error:
        print("ERROR TYPE:", type(error).__name__)
        print("ERROR:", str(error))
