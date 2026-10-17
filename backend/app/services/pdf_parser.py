import pypdfium2 as pdfium


def extract_pages(pdf_bytes: bytes) -> list[str]:
    pdf = pdfium.PdfDocument(pdf_bytes)
    pages = []
    for page in pdf:
        text = page.get_textpage().get_text_range()
        pages.append(text.strip())
    return pages
