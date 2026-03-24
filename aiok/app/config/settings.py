"""Application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]


@dataclass(frozen=True, slots=True)
class Settings:
    """Application settings."""

    # App
    app_name: str = os.getenv("APP_NAME", "AIOK")
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")
    cors_origins: list[str] = field(default_factory=_cors_origins)

    # API Key (optional)
    api_key: str | None = os.getenv("API_KEY")

    # Database
    database_url: str | None = os.getenv("DATABASE_URL")

    # Google Vertex AI
    google_genai_use_vertexai: bool = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true"
    google_application_credentials: str | None = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    google_cloud_project: str | None = os.getenv("GOOGLE_CLOUD_PROJECT")
    google_cloud_location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    # Google Gemini API (fallback)
    google_api_key: str | None = os.getenv("GOOGLE_API_KEY")

    # Model
    model: str = os.getenv("MODEL", "gemini-2.0-flash")

    # MCP
    enable_calendar_mcp: bool = os.getenv("ENABLE_CALENDAR_MCP", "false").lower() == "true"
    enable_github_mcp: bool = os.getenv("ENABLE_GITHUB_MCP", "false").lower() == "true"
    enable_notion_mcp: bool = os.getenv("ENABLE_NOTION_MCP", "false").lower() == "true"
    github_token: str | None = os.getenv("GITHUB_TOKEN")
    github_repo: str = os.getenv("GITHUB_REPO", "catherinejo/aiok_first_project")
    notion_token: str | None = os.getenv("NOTION_TOKEN")
    notion_page_id: str | None = os.getenv("NOTION_PAGE_ID")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()
