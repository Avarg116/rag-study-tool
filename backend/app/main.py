from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import init_db
from app.routers import documents, query

app = FastAPI(title="RAG Study Tool")
app.state.limiter = query.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(documents.router)
app.include_router(query.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}
