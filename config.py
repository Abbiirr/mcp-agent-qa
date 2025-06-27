# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # ─── Your existing settings ──────────────────────────────

    LLM_ENDPOINT: str
    DATABASE_URL: str

    # ─── Tell Pydantic-Settings how to load .env ─────────────
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# one global Settings instance
settings = Settings()
