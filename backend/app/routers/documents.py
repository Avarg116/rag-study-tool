import uuid
from pathlib import Path

import psycopg
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from app.config import settings
from app.database import get_db
from app.schemas import DocumentOut
from app.services.pdf_parser import extract_pages
from app.services.chunker import chunk_pages
from app.services.embeddings import embed_texts

router = APIRouter(prefix="/documents", tags=["documents"])

def pdf_path(document_id):
    return Path(settings.pdf_dir) / f"{document_id}.pdf"

@router.post("/upload", response_model=DocumentOut)
def upload_document(
    file: UploadFile = File(...), conn: psycopg.Connection = Depends(get_db)
):
    if settings.demo_mode:
        raise HTTPException(status_code=403, detail="Uploading is turned off in the demo.")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    pdf_bytes = file.file.read()
    try:
        pages = extract_pages(pdf_bytes)
    except Exception:
        raise HTTPException(status_code=422, detail="This file couldn't be read as a PDF.")

    if not any(pages):
        raise HTTPException(status_code=422, detail="No text found in this PDF.")

    chunks = chunk_pages(pages)

    # embed all chunks in 1 batch
    vectors = embed_texts([c["content"] for c in chunks])

    with conn.transaction():
        document = conn.execute(
            """
            INSERT INTO documents (filename, page_count)
            VALUES (%s, %s)
            RETURNING id, filename, uploaded_at, page_count
            """,
            (file.filename, len(pages)),
        ).fetchone()

        for chunk, vector in zip(chunks, vectors):
            conn.execute(
                """
                INSERT INTO chunks (document_id, page_number, chunk_index, content, embedding)
                VALUES (%s, %s, %s, %s, %s::vector)
                """,
                (document["id"], chunk["page_number"], chunk["chunk_index"], chunk["content"], vector),
            )

    # frontend pdf
    path = pdf_path(document["id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pdf_bytes)

    return document

@router.get("/", response_model=list[DocumentOut])
def list_documents(conn: psycopg.Connection = Depends(get_db)):
    return conn.execute(
        """
        SELECT id, filename, uploaded_at, page_count
        FROM documents
        ORDER BY uploaded_at DESC
        """
    ).fetchall()

@router.get("/{document_id}/file")
def get_document_file(document_id: uuid.UUID):
    path = pdf_path(document_id)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(path, media_type="application/pdf")

@router.delete("/{document_id}")
def delete_document(document_id: uuid.UUID, conn: psycopg.Connection = Depends(get_db)):
    if settings.demo_mode:
        raise HTTPException(status_code=403, detail="Deleting is turned off in the demo.")
    deleted = conn.execute(
        "DELETE FROM documents WHERE id = %s RETURNING id", (document_id,)
    ).fetchone()
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found.")
    pdf_path(document_id).unlink(missing_ok=True)
    return {"deleted": str(document_id)}
