import uuid
from datetime import datetime

from pydantic import BaseModel, Field

class DocumentOut(BaseModel):
    id: uuid.UUID
    filename: str
    uploaded_at: datetime
    page_count: int

class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

class SourceChunk(BaseModel):
    document_id: uuid.UUID
    filename: str
    page_number: int
    content: str
    similarity: float

class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
