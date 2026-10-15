from app.services.chunker import chunk_pages

def test_chunks_overlap():
    chunks = chunk_pages(["abcdefghijklmnopqrstuvwxyz"], size=10, overlap=3)
    assert [c["content"] for c in chunks] == ["abcdefghij", "hijklmnopq", "opqrstuvwx", "vwxyz"]

def test_page_numbers():
    chunks = chunk_pages(["abcdefghijklmno", "", "short"], size=10, overlap=3)
    assert [(c["page_number"], c["chunk_index"]) for c in chunks] == [(1, 0), (1, 1), (3, 0)]
