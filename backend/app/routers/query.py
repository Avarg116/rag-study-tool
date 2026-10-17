import psycopg
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings
from app.database import get_db
from app.schemas import QueryRequest, QueryResponse
from app.services.embeddings import embed_text
from app.services.retrieval import generate_answer, vector_search
from app.services.search_agent import run_agent

router = APIRouter(prefix="/query", tags=["query"])

# limit questions per visitor, only in the demo
limiter = Limiter(key_func=get_remote_address, enabled=settings.demo_mode)

@router.post("/", response_model=QueryResponse)
@limiter.limit("10/hour")
def query(request: Request, body: QueryRequest, conn: psycopg.Connection = Depends(get_db)):
    if settings.search_mode == "agent":
        rows = run_agent(conn, body.question)
    else:
        question_vector = embed_text(body.question)
        rows = vector_search(conn, question_vector, settings.top_k)
    if not rows:
        return {"answer": "No documents have been uploaded yet.", "sources": []}

    answer = generate_answer(body.question, rows)
    return {"answer": answer, "sources": rows}
