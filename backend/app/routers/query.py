import psycopg
from fastapi import APIRouter, Depends

from app.config import settings
from app.database import get_db
from app.schemas import QueryRequest, QueryResponse
from app.services.embeddings import embed_text
from app.services.retrieval import generate_answer, vector_search
from app.services.search_agent import run_agent

router = APIRouter(prefix="/query", tags=["query"])

@router.post("/", response_model=QueryResponse)
def query(request: QueryRequest, conn: psycopg.Connection = Depends(get_db)):
    if settings.search_mode == "agent":
        rows = run_agent(conn, request.question)
    else:
        question_vector = embed_text(request.question)
        rows = vector_search(conn, question_vector, settings.top_k)
    if not rows:
        return {"answer": "No documents have been uploaded yet.", "sources": []}

    answer = generate_answer(request.question, rows)
    return {"answer": answer, "sources": rows}
