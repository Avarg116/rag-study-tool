from fastapi import FastAPI

from app.database import init_db
from app.routers import documents

app = FastAPI(title="RAG Study Tool")

app.include_router(documents.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
