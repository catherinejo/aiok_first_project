"""AIOK - AI Orchestration for Work Automation."""

import importlib.metadata
import os

try:
    __version__ = importlib.metadata.version("aiok")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.1.0"


def _ensure_google_credentials() -> None:
    """Google SDK 초기화 전에 인증 환경변수 설정."""
    from aiok.config import get_settings

    settings = get_settings()

    # Vertex AI: Service Account 인증
    if settings.google_genai_use_vertexai:
        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
        if settings.google_application_credentials:
            os.environ.setdefault(
                "GOOGLE_APPLICATION_CREDENTIALS", settings.google_application_credentials
            )
        if settings.google_cloud_project:
            os.environ.setdefault("GOOGLE_CLOUD_PROJECT", settings.google_cloud_project)
        os.environ.setdefault("GOOGLE_CLOUD_LOCATION", settings.google_cloud_location)
    # Gemini API: API 키 인증 (fallback)
    elif settings.google_api_key and "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = settings.google_api_key


_ensure_google_credentials()

from aiok.agent import aiok_agent

__all__ = ["aiok_agent", "__version__"]
