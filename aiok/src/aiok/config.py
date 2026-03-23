"""Application configuration."""

import importlib.metadata
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_app_version() -> str:
    try:
        return importlib.metadata.version("aiok")
    except importlib.metadata.PackageNotFoundError:
        return "0.1.0"


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "AIOK"
    app_version: str = Field(default_factory=_default_app_version)
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    api_prefix: str = "/api/v1"
    # 쉼표 구분 목록. "*" 이면 모든 오리진 (개발용). 운영에서는 명시적 도메인 권장.
    cors_origins: str = "*"
    # 설정 시 /chat 등 보호 엔드포인트에 Bearer 또는 X-API-Key 필요
    api_key: str | None = None

    # Database (Session 저장용)
    # postgresql+asyncpg://user:pass@localhost:5432/dbname
    database_url: str | None = None

    # Google Vertex AI
    google_genai_use_vertexai: bool = False
    google_application_credentials: str | None = None
    google_cloud_project: str | None = None
    google_cloud_location: str = "us-central1"

    # Google Gemini API (fallback)
    google_api_key: str | None = None

    # Google Calendar MCP
    enable_calendar_mcp: bool = False


def cors_origin_list(cors_origins: str) -> list[str]:
    raw = cors_origins.strip()
    if raw == "*":
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()
