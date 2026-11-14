import re

import psycopg
from anthropic import Anthropic
from rank_bm25 import BM25Okapi

from app.config import settings
from app.services.embeddings import embed_text

client = Anthropic(api_key=settings.anthropic_api_key)

def vector_search(conn: psycopg.Connection, question_vector, k: int):
    return conn.execute(
        """
        SELECT c.id,
               c.document_id,
               c.page_number,
               c.content,
               d.filename,
               1 - (c.embedding <=> %s::vector) AS similarity
        FROM chunks c
        JOIN documents d ON d.id = c.document_id
        ORDER BY c.embedding <=> %s::vector
        LIMIT %s
        """,
        (question_vector, question_vector, k),
    ).fetchall()

def tokenize(text):
    return re.findall(r"[a-z0-9-]+", text.lower())

def keyword_search(conn, question, k):
    rows = conn.execute("""
        SELECT c.id, c.document_id, c.page_number, c.content, d.filename
        FROM chunks c JOIN documents d ON d.id = c.document_id
    """).fetchall()
    if not rows:
        return []
    bm25 = BM25Okapi([tokenize(row["content"]) for row in rows])
    scores = bm25.get_scores(tokenize(question))
    ranked = sorted(zip(rows, scores), key=lambda pair: pair[1], reverse=True)
    return [row for row, score in ranked[:k] if score > 0]

def hybrid_search(conn, question, k):
    vector_results = vector_search(conn, embed_text(question), 20)
    keyword_results = keyword_search(conn, question, 20)
    scores, chunks = {}, {}
    for results in [vector_results, keyword_results]:
        for rank, row in enumerate(results, start=1):
            scores[row["id"]] = scores.get(row["id"], 0) + 1 / (60 + rank)
            chunks[row["id"]] = row
    best_ids = sorted(scores, key=scores.get, reverse=True)[:k]
    return [chunks[i] for i in best_ids]

def build_prompt(question: str, rows) -> str:
    context = "\n\n".join(
        f"[Source {i}] {row['filename']}, page {row['page_number']}:\n{row['content']}"
        for i, row in enumerate(rows, start=1)
    )
    return f"""Answer the question using only the context below.
If the context doesn't contain the answer, say you don't know.
Mention which source you used, like [Source 2].

Context:
{context}

Question: {question}"""

def generate_answer(question: str, rows) -> str:
    response = client.messages.create(
        model=settings.generation_model,
        max_tokens=2048,
        messages=[{"role": "user", "content": build_prompt(question, rows)}],
    )
    return response.content[0].text
