from sentence_transformers import SentenceTransformer

from app.config import settings

model = SentenceTransformer(settings.embedding_model_name)


def embed_texts(texts: list[str]) -> list[list[float]]:
    return model.encode(texts).tolist()


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
