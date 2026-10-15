from app.config import settings


def chunk_pages(pages: list[str], size=None, overlap=None) -> list[dict]:
    size = size or settings.chunk_size_chars
    overlap = overlap or settings.chunk_overlap_chars

    chunks = []
    for page_number, text in enumerate(pages, start=1):
        for i, start in enumerate(range(0, len(text), size - overlap)):
            chunks.append({
                "page_number": page_number,
                "chunk_index": i,
                "content": text[start:start + size].strip(),
            })
            if start + size >= len(text):
                break
    return chunks
