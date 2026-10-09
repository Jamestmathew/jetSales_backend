import cohere

from app.core.config import COHERE_API_KEY


co = cohere.ClientV2(
    api_key=COHERE_API_KEY
)


def generate_embeddings(
    texts: list[str],
    input_type: str = "search_document",
) -> list[list[float]]:
    """
    Generate Cohere embeddings.

    Args:
        texts:
            List of text to embed.

        input_type:
            "search_document" when embedding document chunks.
            "search_query" when embedding user questions.

    Returns:
        List of 1024-dimensional embedding vectors.
    """

    if not texts:
        return []

    response = co.embed(
        model="embed-v4.0",
        input_type=input_type,
        texts=texts,
        output_dimension=1024,
        embedding_types=["float"],
    )

    return response.embeddings.float