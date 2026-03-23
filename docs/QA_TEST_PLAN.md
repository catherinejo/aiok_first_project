# QA 테스트 계획서

**프로젝트**: AIOK (AI Orchestration for Work Automation)
**작성일**: 2026-03-23
**버전**: 1.0.0

---

## 1. 테스트 개요

### 1.1 테스트 목적
- AIOK 시스템의 품질 보증
- 각 에이전트 기능의 정확성 검증
- API 안정성 및 신뢰성 확인
- 사용자 시나리오 기반 E2E 검증

### 1.2 테스트 범위

| 구분 | 포함 | 제외 |
|------|------|------|
| 기능 테스트 | 번역, 메일, 회의록, 캘린더, 일반 응답 | - |
| API 테스트 | /chat, /health, 개별 에이전트 엔드포인트 | - |
| 통합 테스트 | ADK Runner + FastAPI | 외부 MCP 서버 |
| 성능 테스트 | 응답 시간, 동시 사용자 | 부하 테스트 (Phase 2) |
| UI 테스트 | - | Phase 5 이후 |

---

## 2. 테스트 전략

### 2.1 테스트 레벨

```
┌─────────────────────────────────────────┐
│          E2E 테스트 (Playwright)         │  ← Phase 5 이후
├─────────────────────────────────────────┤
│          통합 테스트 (pytest)            │  ← Phase 3-4
├─────────────────────────────────────────┤
│          단위 테스트 (pytest)            │  ← Phase 2
└─────────────────────────────────────────┘
```

### 2.2 테스트 도구

| 도구 | 용도 |
|------|------|
| pytest | 단위/통합 테스트 |
| pytest-asyncio | 비동기 테스트 |
| httpx | API 테스트 클라이언트 |
| pytest-cov | 커버리지 측정 |
| Playwright | E2E 테스트 (UI) |

---

## 3. 테스트 케이스

### 3.1 단위 테스트

#### 3.1.1 번역 도구 (translate_text)

| TC ID | 테스트 케이스 | 입력 | 기대 결과 |
|-------|--------------|------|----------|
| TR-001 | 한→영 번역 | text="안녕하세요", target="en" | 영어 번역 결과 반환 |
| TR-002 | 영→한 번역 | text="Hello", target="ko" | 한국어 번역 결과 반환 |
| TR-003 | 자동 언어 감지 | text="こんにちは", source="auto" | 일본어 감지 |
| TR-004 | 빈 텍스트 | text="" | 에러 또는 빈 결과 |
| TR-005 | 긴 텍스트 (5000자) | 긴 텍스트 | 정상 처리 |

#### 3.1.2 메일 도구 (summarize_email, generate_reply)

| TC ID | 테스트 케이스 | 입력 | 기대 결과 |
|-------|--------------|------|----------|
| EM-001 | 메일 요약 | 일반 비즈니스 메일 | 핵심 포인트 추출 |
| EM-002 | 액션 아이템 추출 | "~까지 제출해주세요" 포함 메일 | 액션 아이템 감지 |
| EM-003 | 긴급 메일 감지 | "긴급", "ASAP" 포함 | urgent 감정 감지 |
| EM-004 | 회신 생성 (formal) | tone="formal" | 격식체 회신 |
| EM-005 | 회신 생성 (friendly) | tone="friendly" | 친근한 회신 |

#### 3.1.3 회의록 도구 (summarize_meeting)

| TC ID | 테스트 케이스 | 입력 | 기대 결과 |
|-------|--------------|------|----------|
| MT-001 | 일반 회의 요약 | 회의 녹취록 | 요약 + 결정사항 |
| MT-002 | 스탠드업 회의 | meeting_type="standup" | 진행/계획/블로커 구분 |
| MT-003 | 액션 아이템 추출 | "홍길동님이 ~하기로" | 담당자 + 태스크 추출 |
| MT-004 | 빈 내용 | content="" | 에러 처리 |

#### 3.1.4 캘린더 MCP (Calendar MCP - 별도 설정 시)

| TC ID | 테스트 케이스 | 입력 | 기대 결과 |
|-------|--------------|------|----------|
| CA-001 | 일정 조회 | 오늘 날짜 | 일정 목록 반환 |
| CA-002 | 일정 생성 | 제목, 시작/종료 시간 | 이벤트 생성 확인 |
| CA-003 | 일정 수정 | event_id + 새 제목 | 수정 확인 |
| CA-004 | 일정 삭제 | event_id | 삭제 확인 |
| CA-005 | MCP 연결 실패 | MCP 서버 중단 | 적절한 에러 메시지 |

---

### 3.2 통합 테스트

#### 3.2.1 API 엔드포인트

| TC ID | 테스트 케이스 | Method | Path | 기대 결과 |
|-------|--------------|--------|------|----------|
| API-001 | 헬스체크 | GET | /health | 200 + status: healthy |
| API-002 | 채팅 - 일반 질문 | POST | /api/v1/chat | 200 + 응답 |
| API-003 | 채팅 - 번역 요청 | POST | /api/v1/chat | 번역 도구 사용 |
| API-004 | 채팅 - 세션 유지 | POST | /api/v1/chat | 동일 session_id 유지 |
| API-005 | 잘못된 요청 | POST | /api/v1/chat | 422 Validation Error |
| API-006 | 빈 메시지 | POST | /api/v1/chat | 에러 처리 |

#### 3.2.2 ADK Runner 통합

| TC ID | 테스트 케이스 | 기대 결과 |
|-------|--------------|----------|
| ADK-001 | Runner 초기화 | 정상 초기화 |
| ADK-002 | 세션 생성 | 세션 ID 반환 |
| ADK-003 | 도구 호출 | 도구 실행 결과 반환 |
| ADK-004 | 멀티턴 대화 | 컨텍스트 유지 |
| ADK-005 | 에러 복구 | Graceful 에러 처리 |

---

### 3.3 E2E 테스트 (Phase 5 이후)

| TC ID | 시나리오 | 단계 |
|-------|---------|------|
| E2E-001 | 번역 플로우 | 1. 채팅창 열기 → 2. "영어로 번역해줘: 안녕" 입력 → 3. 번역 결과 확인 |
| E2E-002 | 메일 처리 플로우 | 1. 메일 패널 선택 → 2. 메일 붙여넣기 → 3. 요약 + 회신 확인 |
| E2E-003 | 회의록 플로우 | 1. 회의록 입력 → 2. 요약 결과 확인 → 3. 액션 아이템 확인 |
| E2E-004 | 세션 유지 | 1. 대화 진행 → 2. 이전 대화 참조 질문 → 3. 컨텍스트 유지 확인 |

---

## 4. 테스트 환경

### 4.1 환경 구성

| 환경 | 용도 | 설정 |
|------|------|------|
| Local | 개발자 테스트 | uv run pytest |
| CI | 자동화 테스트 | GitHub Actions |
| Staging | 통합 테스트 | GCP (예정) |

### 4.2 테스트 데이터

```
tests/
├── fixtures/
│   ├── emails/           # 테스트용 메일 샘플
│   │   ├── formal.txt
│   │   ├── urgent.txt
│   │   └── with_action_items.txt
│   ├── meetings/         # 테스트용 회의록 샘플
│   │   ├── standup.txt
│   │   ├── planning.txt
│   │   └── review.txt
│   └── translations/     # 번역 테스트 샘플
│       ├── ko_text.txt
│       ├── en_text.txt
│       └── ja_text.txt
└── conftest.py           # pytest fixtures
```

---

## 5. 품질 기준

### 5.1 커버리지 목표

| 구분 | 목표 |
|------|------|
| 단위 테스트 | 80% 이상 |
| 통합 테스트 | 70% 이상 |
| 전체 | 75% 이상 |

### 5.2 성능 기준

| 항목 | 기준 |
|------|------|
| API 응답 시간 (일반) | < 3초 |
| API 응답 시간 (복잡) | < 10초 |
| 에러율 | < 1% |

### 5.3 합격 기준

- [ ] 모든 Critical 테스트 케이스 통과
- [ ] 커버리지 목표 달성
- [ ] 성능 기준 충족
- [ ] 보안 취약점 없음

---

## 6. 테스트 일정

| Phase | 테스트 유형 | 시기 |
|-------|------------|------|
| Phase 2 | 단위 테스트 작성 | 에이전트 개발 완료 후 |
| Phase 3-4 | 통합 테스트 작성 | API 개발 완료 후 |
| Phase 5 | E2E 테스트 작성 | UI 개발 완료 후 |
| Phase 6 | 전체 회귀 테스트 | 상용화 전 |

---

## 7. 리스크 및 대응

| 리스크 | 영향 | 대응 방안 |
|--------|------|----------|
| Google API 할당량 초과 | 테스트 실패 | Mock 응답 사용 |
| MCP 서버 불안정 | 캘린더 테스트 실패 | MCP 테스트 분리 |
| 비동기 테스트 복잡성 | 테스트 지연 | pytest-asyncio 활용 |

---

## 8. 테스트 코드 예시

```python
# tests/test_tools/test_translation.py
import pytest
from aiok.tools.translation import translate_text


def test_translate_text_returns_dict():
    result = translate_text(
        text="안녕하세요",
        target_language="en",
    )
    assert isinstance(result, dict)
    assert "original" in result
    assert "target_language" in result


def test_translate_text_with_style():
    result = translate_text(
        text="Hello",
        target_language="ko",
        style="formal",
    )
    assert result["style"] == "formal"
```

```python
# tests/test_api/test_chat.py
import pytest
from httpx import AsyncClient
from aiok.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
```

---

*QA 담당 작성: 2026-03-23*
