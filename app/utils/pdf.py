from pypdf import PdfReader
import io
def extract_text_from_pdf(file_bytes: bytes) -> str:
    
    text_chunks = []
    pdf_stream = io.BytesIO(file_bytes)
    reader = PdfReader(pdf_stream)


    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_chunks.append(page_text)


    return "\n".join(text_chunks)