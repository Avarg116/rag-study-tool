from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from app.config import settings

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

def init_db() -> None:
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        conn.execute(SCHEMA_PATH.read_text())

def get_db():
    conn = psycopg.connect(
        settings.database_url, autocommit=True, row_factory=dict_row
    )
    try:
        yield conn
    finally:
        conn.close()
