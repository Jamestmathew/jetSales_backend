from app.services.context_builder import build_context


structured_data = {
    "offering_id": "123",
    "name": "AI Business Assistant",
    "type": "product",
    "price": 150000,
    "currency": "NGN",
    "available": True,
}


rag_results = [
    {
        "content": (
            "The AI Business Assistant is a website "
            "assistant that helps businesses answer "
            "customer questions and capture leads."
        ),
        "similarity": 0.82,
    }
]


context = build_context(
    structured_data=structured_data,
    rag_results=rag_results,
)


print("=" * 60)
print("BUILT CONTEXT")
print("=" * 60)
print(context)
