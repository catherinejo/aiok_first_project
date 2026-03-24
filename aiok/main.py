"""AIOK - FastAPI + Google ADK 통합."""

from __future__ import annotations

import logging
import os
import uuid
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, AsyncGenerator

from fastapi import APIRouter, Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google.adk import Runner
from google.adk.apps import App
from google.adk.errors.already_exists_error import AlreadyExistsError
from google.adk.events.event import Event
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from google.genai import types
from pydantic import BaseModel

from app.agent.root import root_agent
from app.config.settings import settings
from app.tool import SUPPORTED_EXTENSIONS, is_supported_file, parse_file

# 환경변수 설정 (Google SDK 초기화 전)
if settings.google_genai_use_vertexai:
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
    if settings.google_application_credentials:
        os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", settings.google_application_credentials)
    if settings.google_cloud_project:
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", settings.google_cloud_project)
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", settings.google_cloud_location)
elif settings.google_api_key and "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = settings.google_api_key


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# =============================================================================
# Models
# =============================================================================

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str = "default_user"
    file_ids: list[str] | None = None


class ChatResponse(BaseModel):
    session_id: str
    response: str


class SessionInfo(BaseModel):
    session_id: str
    user_id: str
    created_at: str | None = None
    last_message: str | None = None


class MessageInfo(BaseModel):
    role: str
    content: str


class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: list[MessageInfo]


class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    content_preview: str
    char_count: int


# =============================================================================
# Global State
# =============================================================================

runner: Runner | None = None
session_service: DatabaseSessionService | InMemorySessionService | None = None
session_metadata: dict[str, dict] = {}
uploaded_files: dict[str, list[dict]] = {}


# =============================================================================
# Helpers
# =============================================================================

def _final_response_text(event: Event) -> str:
    """최종 응답 이벤트에서 사용자에게 보여줄 텍스트만 추출."""
    if not event.content or not event.content.parts:
        return ""
    return "".join(
        part.text
        for part in event.content.parts
        if part.text and not part.thought
    )


def require_api_key_if_configured(
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    if not settings.api_key:
        return
    token: str | None = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif x_api_key:
        token = x_api_key.strip()
    if not token or token != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# =============================================================================
# App Factory
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan."""
    global runner, session_service

    logger.info("Starting %s", settings.app_name)

    adk_app = App(name="aiok", root_agent=root_agent)

    if settings.database_url:
        logger.info("Using DatabaseSessionService (PostgreSQL)")
        session_service = DatabaseSessionService(db_url=settings.database_url)
    else:
        logger.info("Using InMemorySessionService (sessions will be lost on restart)")
        session_service = InMemorySessionService()

    runner = Runner(app=adk_app, session_service=session_service)

    yield

    logger.info("Shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="업무자동화 AI Agent",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_origins != ["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    router = APIRouter(
        prefix=settings.api_prefix,
        dependencies=[Depends(require_api_key_if_configured)],
    )

    @router.get("/sessions", response_model=list[SessionInfo])
    async def list_sessions(user_id: str = "default_user"):
        sessions = [
            SessionInfo(
                session_id=sid,
                user_id=meta["user_id"],
                created_at=meta.get("created_at"),
                last_message=meta.get("last_message"),
            )
            for sid, meta in session_metadata.items()
            if meta["user_id"] == user_id
        ]
        sessions.sort(key=lambda s: s.created_at or "", reverse=True)
        return sessions

    @router.get("/sessions/{session_id}/messages", response_model=SessionHistoryResponse)
    async def get_session_history(session_id: str, user_id: str = "default_user"):
        if runner is None or session_service is None:
            raise HTTPException(status_code=503, detail="Agent runner not ready")

        session = await session_service.get_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id,
        )

        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")

        messages = []
        if hasattr(session, 'events') and session.events:
            for event in session.events:
                if event.content and event.content.parts:
                    text = "".join(
                        part.text for part in event.content.parts
                        if hasattr(part, 'text') and part.text
                    )
                    if text:
                        role = event.content.role or "assistant"
                        messages.append(MessageInfo(role=role, content=text))

        return SessionHistoryResponse(session_id=session_id, messages=messages)

    @router.post("/upload", response_model=FileUploadResponse)
    async def upload_file(
        file: UploadFile = File(...),
        session_id: str | None = None,
    ):
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        if not is_supported_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: {', '.join(SUPPORTED_EXTENSIONS)}",
            )

        try:
            content = await file.read()
            extracted_text = parse_file(file.filename, content)
        except Exception as e:
            logger.exception("Failed to parse file: %s", file.filename)
            raise HTTPException(status_code=400, detail=f"Failed to parse file: {e!s}") from None

        file_id = str(uuid.uuid4())
        sid = session_id or "pending"

        if sid not in uploaded_files:
            uploaded_files[sid] = []
        uploaded_files[sid].append({
            "file_id": file_id,
            "filename": file.filename,
            "content": extracted_text,
        })

        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            content_preview=extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text,
            char_count=len(extracted_text),
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
                session_metadata[session_id] = {
                    "user_id": request.user_id,
                    "created_at": datetime.now().isoformat(),
                    "last_message": request.message[:50],
                }
            except AlreadyExistsError:
                pass
        else:
            if session_id in session_metadata:
                session_metadata[session_id]["last_message"] = request.message[:50]

        # 첨부파일 내용 포함
        message_text = request.message
        if request.file_ids:
            file_contents = []
            for sid in ["pending", session_id]:
                if sid in uploaded_files:
                    for f in uploaded_files[sid]:
                        if f["file_id"] in request.file_ids:
                            file_contents.append(f"[첨부파일: {f['filename']}]\n{f['content']}")
            if file_contents:
                message_text = "\n\n".join(file_contents) + "\n\n---\n\n" + request.message
                if "pending" in uploaded_files:
                    if session_id not in uploaded_files:
                        uploaded_files[session_id] = []
                    uploaded_files[session_id].extend(uploaded_files.pop("pending", []))

        user_message = types.Content(
            role="user",
            parts=[types.Part(text=message_text)],
        )

        response_text = ""
        last_error = ""
        max_attempts = 2
        for attempt in range(1, max_attempts + 1):
            try:
                async for event in runner.run_async(
                    user_id=request.user_id,
                    session_id=session_id,
                    new_message=user_message,
                ):
                    if event.is_final_response() and event.content:
                        response_text = _final_response_text(event)
                break
            except Exception as e:
                last_error = str(e)
                is_quota_error = "RESOURCE_EXHAUSTED" in last_error or "429" in last_error
                if is_quota_error and attempt < max_attempts:
                    logger.warning(
                        "Agent quota hit (attempt=%s/%s), retrying after backoff...",
                        attempt,
                        max_attempts,
                    )
                    await asyncio.sleep(3)
                    continue
                logger.exception(
                    "Agent run failed (user_id=%s, session_id=%s): %s",
                    request.user_id,
                    session_id,
                    last_error,
                )
                raise HTTPException(status_code=502, detail=f"Agent execution failed: {last_error}") from None

        return ChatResponse(
            session_id=session_id,
            response=response_text or "응답 없음",
        )

    app.include_router(router)
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
