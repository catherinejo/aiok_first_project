"""AIOK - FastAPI + Google ADK 통합."""

import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator

# Google SDK 초기화 전에 환경변수 설정 필요
# pydantic-settings가 .env를 읽지만 os.environ에 설정하지 않으므로 수동 설정
from aiok.config import cors_origin_list, get_settings

_settings = get_settings()

# Vertex AI: Service Account 인증
if _settings.google_genai_use_vertexai:
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
    if _settings.google_application_credentials:
        os.environ.setdefault(
            "GOOGLE_APPLICATION_CREDENTIALS", _settings.google_application_credentials
        )
    if _settings.google_cloud_project:
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", _settings.google_cloud_project)
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", _settings.google_cloud_location)
# Gemini API: API 키 인증 (fallback)
elif _settings.google_api_key and "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = _settings.google_api_key

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.adk import Runner
from google.adk.apps import App
from google.adk.errors.already_exists_error import AlreadyExistsError
from google.adk.events.event import Event
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from google.genai import types
from pydantic import BaseModel

from aiok.agent import aiok_agent

logger = logging.getLogger(__name__)

# uvicorn이 로거를 설정하지만, 라이브러리 기본 외에 메시지가 보이도록 레벨만 맞춤
logging.basicConfig(level=logging.INFO)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str = "default_user"


class ChatResponse(BaseModel):
    session_id: str
    response: str


def _final_response_text(event: Event) -> str:
    """최종 응답 이벤트에서 사용자에게 보여줄 텍스트만 추출 (ADK llm_agent 패턴)."""
    if not event.content or not event.content.parts:
        return ""
    return "".join(
        part.text
        for part in event.content.parts
        if part.text and not part.thought
    )


runner: Runner | None = None
session_service: DatabaseSessionService | InMemorySessionService | None = None


def require_api_key_if_configured(
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    settings = get_settings()
    if not settings.api_key:
        return
    token: str | None = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif x_api_key:
        token = x_api_key.strip()
    if not token or token != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan."""
    global runner, session_service
    settings = get_settings()

    logger.info("Starting %s v%s", settings.app_name, settings.app_version)

    adk_app = App(name="aiok", root_agent=aiok_agent)

    # Session Service 선택: DB URL이 있으면 DatabaseSessionService, 없으면 InMemory
    if settings.database_url:
        logger.info("Using DatabaseSessionService (PostgreSQL)")
        session_service = DatabaseSessionService(db_url=settings.database_url)
    else:
        logger.info("Using InMemorySessionService (sessions will be lost on restart)")
        session_service = InMemorySessionService()

    runner = Runner(
        app=adk_app,
        session_service=session_service,
    )

    yield

    logger.info("Shutting down")


def create_app() -> FastAPI:
    settings = get_settings()
    origins = cors_origin_list(settings.cors_origins)
    allow_credentials = settings.cors_origins.strip() != "*"

    app = FastAPI(
        title=settings.app_name,
        description="업무자동화 AI Agent",
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        return {"status": "healthy", "version": settings.app_version}

    router = APIRouter(
        prefix=settings.api_prefix,
        dependencies=[Depends(require_api_key_if_configured)],
    )

    @router.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        if runner is None or session_service is None:
            raise HTTPException(status_code=503, detail="Agent runner not ready")

        session_id = request.session_id or str(uuid.uuid4())
        app_name = runner.app_name

        existing_session = await session_service.get_session(
            app_name=app_name,
            user_id=request.user_id,
            session_id=session_id,
        )
        if existing_session is None:
            try:
                await session_service.create_session(
                    app_name=app_name,
                    user_id=request.user_id,
                    session_id=session_id,
                )
            except AlreadyExistsError:
                pass

        user_message = types.Content(
            role="user",
            parts=[types.Part(text=request.message)],
        )

        response_text = ""
        try:
            async for event in runner.run_async(
                user_id=request.user_id,
                session_id=session_id,
                new_message=user_message,
            ):
                if event.is_final_response() and event.content:
                    response_text = _final_response_text(event)
        except Exception:
            logger.exception(
                "Agent run failed (user_id=%s, session_id=%s)",
                request.user_id,
                session_id,
            )
            raise HTTPException(
                status_code=502,
                detail="Agent execution failed",
            ) from None

        return ChatResponse(
            session_id=session_id,
            response=response_text or "응답 없음",
        )

    app.include_router(router)
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run("aiok.main:app", host=settings.host, port=settings.port, reload=settings.debug)
