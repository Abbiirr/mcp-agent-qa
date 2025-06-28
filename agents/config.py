# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # ─── Your existing settings ──────────────────────────────

    LLM_ENDPOINT: str
    DATABASE_URL: str
    MCP_ENDPOINT: Optional[str] = "http://localhost:8000/insert_user"
    USE_MCP: Optional[str] = "false"  # Default to false, can be overridden in .env
    DEVICE_ID: Optional[str] = None
    AUTH_TOKEN: Optional[str] = None

    # ─── Tell Pydantic-Settings how to load .env ─────────────
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# one global Settings instance
settings = Settings()
