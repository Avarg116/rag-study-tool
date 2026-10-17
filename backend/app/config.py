from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://rag_user:rag_password@localhost:5432/rag_study_tool"
    pdf_dir: str = "/data/pdfs"

    anthropic_api_key: str = ""
    generation_model: str = "claude-sonnet-5"
    agent_model: str = "claude-haiku-4-5"

    embedding_model_name: str = "all-MiniLM-L6-v2"
    chunk_size_chars: int = 1200
    chunk_overlap_chars: int = 200
    top_k: int = 5
    search_mode: str = "agent"

    demo_mode: bool = False

settings = Settings()
