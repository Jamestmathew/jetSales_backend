from app.services.pdf import extract_text_from_pdf


pdf_path = "app/jetintel.pdf"

text = extract_text_from_pdf(pdf_path)

print(text)