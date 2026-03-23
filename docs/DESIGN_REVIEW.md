# 설계 검토 보고서

**프로젝트**: AIOK (AI Orchestration for Work Automation)
**검토일**: 2026-03-23
**검토자**: 설계 담당

---

## 1. 검토 요약

| 항목 | 평가 | 비고 |
|------|------|------|
| 아키텍처 설계 | ✅ 적합 | 계층 분리 명확 |
| 에이전트 설계 | ✅ 적합 | SRP 준수, 확장성 확보 |
| 데이터 모델 | ✅ 적합 | Pydantic 활용 적절 |
| API 설계 | ⚠️ 보완 필요 | Calendar API 누락 |
| 에이전트 간 통신 | ⚠️ 보완 필요 | 상세 설계 필요 |
| 에러 처리 | ⚠️ 보완 필요 | 에이전트별 에러 정의 필요 |
| 보안 | ⚠️ 보완 필요 | OAuth 흐름 상세화 필요 |

**종합 평가**: 기본 설계는 적합하나, 일부 보완 필요

---

## 2. 상세 검토

### 2.1 아키텍처 설계 ✅

**강점:**
- 3-tier 아키텍처 (Client → API → Agent) 명확
- Google ADK 기반 오케스트레이션 적절
- 데이터 레이어 추상화로 DB 교체 용이

**개선 권고:**
```
현재: Client → FastAPI → Orchestrator → Agents
권고: Client → FastAPI → [Message Queue] → Orchestrator → Agents
```
- 비동기 처리가 필요한 경우 메시지 큐(Redis/Pub-Sub) 도입 고려
- 현 단계에서는 불필요, Phase 7 이후 검토

---

### 2.2 에이전트 설계 ✅

**강점:**
- 단일 책임 원칙(SRP) 준수
- Calendar Agent 분리로 재사용성 확보
- Base Agent 추상화로 일관성 유지

**개선 권고:**

#### 2.2.1 에이전트 간 통신 패턴 명시 필요

```python
# 권고: 에이전트 간 통신 인터페이스 정의
class AgentMessage(BaseModel):
    """에이전트 간 메시지"""
    from_agent: str
    to_agent: str
    action: str
    payload: dict
    correlation_id: str  # 요청 추적용

class AgentCommunicator(Protocol):
    """에이전트 통신 프로토콜"""
    async def send(self, message: AgentMessage) -> None: ...
    async def request(self, message: AgentMessage) -> AgentMessage: ...
```

#### 2.2.2 에이전트 상태 관리

```python
# 권고: 에이전트 상태 열거형 추가
class AgentStatus(str, Enum):
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    DEGRADED = "degraded"  # 부분 기능만 가능
```

---

### 2.3 데이터 모델 ✅

**강점:**
- Pydantic v2 활용 적절
- 입출력 스키마 명확히 정의
- Optional 필드 적절히 사용

**개선 권고:**

#### 2.3.1 공통 베이스 모델 추가

```python
# 권고: 모든 출력의 공통 필드
class BaseAgentOutput(BaseModel):
    """에이전트 출력 베이스"""
    agent_name: str
    processing_time_ms: int
    model_used: str
    token_usage: Optional[TokenUsage] = None

class TokenUsage(BaseModel):
    """토큰 사용량 (비용 추적용)"""
    input_tokens: int
    output_tokens: int
```

#### 2.3.2 응답 유니온 타입 수정

```python
# 현재 (ChatResponse.response)
response: Union[TranslationOutput, EmailOutput, MeetingOutput, GeneralOutput]

# 권고: CalendarOutput 추가
response: Union[
    TranslationOutput,
    EmailOutput,
    MeetingOutput,
    CalendarOutput,  # 누락됨
    GeneralOutput
]
```

---

### 2.4 API 설계 ⚠️

**문제점:**
1. Calendar API 엔드포인트 누락
2. Streaming 응답 미고려
3. WebSocket 지원 미고려

**권고 수정:**

```python
# 추가 필요 엔드포인트
| POST | `/api/v1/calendar/events` | 캘린더 이벤트 관리 |
| GET  | `/api/v1/calendar/events` | 이벤트 목록 조회 |
| WS   | `/api/v1/chat/stream`     | 스트리밍 채팅 (선택) |
```

**스트리밍 API 권고:**

```python
# SSE (Server-Sent Events) 지원
@router.post("/api/v1/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        async for chunk in orchestrator.stream_response(request):
            yield f"data: {chunk.model_dump_json()}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

### 2.5 에이전트 간 통신 ⚠️

**문제점:**
- Meeting → Calendar 연동 흐름은 명시되었으나 구현 방식 미정의
- 순환 호출 방지 로직 없음

**권고 설계:**

```python
# 에이전트 간 호출 관리자
class AgentOrchestrator:
    MAX_AGENT_HOPS = 3  # 최대 에이전트 체인 깊이

    async def delegate_to_agent(
        self,
        from_agent: str,
        to_agent: str,
        payload: dict,
        hop_count: int = 0
    ) -> AgentOutput:
        if hop_count >= self.MAX_AGENT_HOPS:
            raise AgentChainLimitExceeded()

        # 호출 체인 로깅
        logger.info(f"Agent delegation: {from_agent} → {to_agent} (hop: {hop_count})")

        target = self.get_agent(to_agent)
        return await target.execute(payload, hop_count=hop_count + 1)
```

---

### 2.6 에러 처리 ⚠️

**문제점:**
- 에이전트별 구체적 에러 코드 미정의
- Graceful degradation 로직 미상세

**권고 추가:**

```python
# 에이전트별 에러 코드
AGENT_ERROR_CODES = {
    # Translation Agent
    "TR001": "Unsupported language pair",
    "TR002": "Text too long for translation",
    "TR003": "Language detection failed",

    # Email Agent
    "EM001": "Invalid email format",
    "EM002": "Email content too short",

    # Meeting Agent
    "MT001": "Meeting content not recognized",
    "MT002": "No action items found",

    # Calendar Agent
    "CA001": "Calendar API authentication failed",
    "CA002": "Invalid date/time format",
    "CA003": "Event conflict detected",
    "CA004": "Calendar not found",

    # General
    "GN001": "Query too vague",
}

# Fallback 전략
class FallbackStrategy:
    """에이전트 장애 시 폴백 전략"""

    FALLBACK_MAP = {
        "translation": "general",  # 번역 실패 시 General이 번역 시도
        "email": "general",
        "meeting": "general",
        "calendar": None,  # 캘린더는 폴백 불가 (외부 API 의존)
    }
```

---

### 2.7 보안 ⚠️

**문제점:**
- Google Calendar OAuth 흐름 미상세
- API Key 저장/관리 방식 미정의

**권고 추가:**

```python
# OAuth 흐름 (Google Calendar)
"""
1. 사용자 최초 접근
   → /api/v1/auth/google/init 호출
   → Google OAuth 페이지로 리다이렉트

2. OAuth 콜백
   → /api/v1/auth/google/callback
   → Access Token + Refresh Token 저장

3. 토큰 관리
   → Refresh Token으로 Access Token 자동 갱신
   → 토큰은 암호화하여 저장
"""

class OAuthConfig(BaseModel):
    """OAuth 설정"""
    client_id: str
    client_secret: SecretStr  # Pydantic SecretStr 사용
    redirect_uri: str
    scopes: List[str] = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events"
    ]
```

---

## 3. 추가 권고 사항

### 3.1 관찰성 (Observability)

```python
# 모든 에이전트 호출에 추적 ID 포함
class RequestContext(BaseModel):
    """요청 컨텍스트"""
    trace_id: str  # 전체 요청 추적
    span_id: str   # 개별 에이전트 호출 추적
    user_id: str
    session_id: str
```

### 3.2 Rate Limiting 상세화

```python
# 에이전트별 Rate Limit (분당)
RATE_LIMITS = {
    "translation": 60,
    "email": 30,
    "meeting": 20,
    "calendar": 100,  # Google API 할당량 고려
    "general": 60,
}
```

### 3.3 캐싱 전략

```python
# 캐싱 가능 항목
CACHEABLE = {
    "translation": True,   # 동일 텍스트 번역 캐싱
    "email": False,        # 매번 새로운 응답 필요
    "meeting": False,      # 매번 새로운 응답 필요
    "calendar": True,      # 일정 조회 결과 캐싱 (TTL: 5분)
    "general": False,      # 컨텍스트 의존적
}
```

---

## 4. 수정 필요 항목 체크리스트

| 우선순위 | 항목 | 설명 |
|----------|------|------|
| 🔴 높음 | Calendar API 엔드포인트 추가 | 명세서에 누락됨 |
| 🔴 높음 | ChatResponse.response에 CalendarOutput 추가 | 유니온 타입 누락 |
| 🟡 중간 | 에이전트 간 통신 인터페이스 정의 | 구현 시 필요 |
| 🟡 중간 | 에이전트별 에러 코드 정의 | 디버깅에 필수 |
| 🟡 중간 | OAuth 흐름 상세화 | Calendar Agent 구현 시 필요 |
| 🟢 낮음 | Streaming API 설계 | UX 개선용, 추후 추가 가능 |
| 🟢 낮음 | 캐싱 전략 상세화 | 성능 최적화 단계에서 적용 |

---

## 5. 결론

현재 설계는 **MVP(최소 기능 제품) 개발에 충분**하며, 위 권고 사항은 개발 진행 중 점진적으로 반영 가능합니다.

**즉시 수정 필요 항목:**
1. Calendar API 엔드포인트 추가
2. ChatResponse 유니온 타입 수정

**다음 단계 진행 가능**: 개발 구조 설계 및 Phase 1 착수

---

*검토 완료: 2026-03-23*
