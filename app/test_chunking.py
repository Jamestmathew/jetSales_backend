from app.services.pdf import extract_text_from_pdf
from app.services.cleaning import clean_text
from app.services.chunking import chunk_text
from app.services.embeddings import generate_embeddings


pdf_path = "app/jetintel.pdf"


raw_text = extract_text_from_pdf(pdf_path)

cleaned_text = clean_text(raw_text)

chunks = chunk_text(
    cleaned_text,
    chunk_size=1000,
    chunk_overlap=200
)

print(f"Total chunks: {len(chunks)}")


embeddings = generate_embeddings(chunks)

print(f"Total embeddings: {len(embeddings)}")


if embeddings:
    print(f"Embedding dimensions: {len(embeddings[0])}")
    print("First 10 values:")
    print(embeddings[0][:10])