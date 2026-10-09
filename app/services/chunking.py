import re


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into simple sentence-like units.
    """

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    return [sentence.strip() for sentence in sentences if sentence.strip()]


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> list[str]:
    """
    Split text into natural, overlapping chunks.

    The function tries to keep sentences together instead of
    cutting words in the middle.
    """

    if not text.strip():
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    # Clean excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()

    sentences = split_into_sentences(text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:

        # If adding the sentence still fits
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk = (
                f"{current_chunk} {sentence}"
                if current_chunk
                else sentence
            )

        else:
            # Save the current chunk
            if current_chunk:
                chunks.append(current_chunk.strip())

            # Create overlap from the end of previous chunk
            overlap_text = ""

            words = current_chunk.split()

            for word in reversed(words):
                if len(overlap_text) + len(word) + 1 > chunk_overlap:
                    break

                overlap_text = (
                    f"{word} {overlap_text}"
                    if overlap_text
                    else word
                )

            current_chunk = (
                f"{overlap_text} {sentence}".strip()
            )

    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks