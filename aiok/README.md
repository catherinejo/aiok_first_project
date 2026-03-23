# AIOK - AI Orchestration for Work Automation

업무자동화 AI Agent 오케스트레이션 시스템

## 기능

- 통번역 (한/영/일/중)
- 메일 요약 및 회신 초안 생성
- 회의록 요약 및 액션 아이템 추출
- Google Calendar 연동 일정 관리

## 설치

```bash
uv sync
```

## 실행

```bash
uv run uvicorn aiok.main:app --reload
```

- API: `POST /api/v1/chat` (본문: `message`, 선택 `session_id`, `user_id`)
- 헬스: `GET /health`
- `.env.example`을 참고해 `GOOGLE_API_KEY` 설정 (필수)
- 운영에서 API를 막으려면 `API_KEY`를 설정하고 요청에 `Authorization: Bearer <키>` 또는 `X-API-Key` 추가
- `CORS_ORIGINS`는 운영에서 특정 도메인 목록 권장 (`*`와 브라우저 credentials는 함께 쓰지 않도록 앱에서 처리)

## 기술 스택

- Python 3.11+
- Google ADK
- FastAPI
- Pydantic
