import psycopg
from anthropic import Anthropic

from app.config import settings

client = Anthropic(api_key=settings.anthropic_api_key)

def vector_search(conn: psycopg.Connection, question_vector, k: int):
    return conn.execute(
        """
        SELECT c.page_number,
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
