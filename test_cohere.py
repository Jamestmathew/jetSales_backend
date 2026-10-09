
from app.services.embeddings import generate_embeddings


try:
    embeddings = generate_embeddings(
        ["JetSale helps businesses answer customer questions."],
        input_type="search_query",
    )

    print("Embedding request succeeded.")
    print("Number of embeddings:", len(embeddings))
    print("Embedding dimensions:", len(embeddings[0]))

except Exception as error:
    print("Embedding request failed.")
    print("Error type:", type(error).__name__)
    print("Error message:", str(error))
    