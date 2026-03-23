# 업무자동화 AI Agent 오케스트레이션 시스템 개발 명세서

**프로젝트명**: AI Orchestration for Work Automation (AIOK)
**버전**: 1.0.0
**작성일**: 2026-03-23
**상태**: Draft

---

## 1. 프로젝트 개요

### 1.1 목적
회사 업무 효율성 향상을 위한 AI 에이전트 오케스트레이션 시스템 구축

### 1.2 핵심 기능
| 기능 | 설명 |
|------|------|
| 통번역 | 다국어 문서/텍스트 번역 및 통역 지원 |
| 메일 요약/회신 | 이메일 내용 요약 및 회신 초안 자동 생성 |
| 회의록 요약 | 회의 내용 요약 및 핵심 사항 추출 |
| 캘린더 관리 | Google Calendar 연동 일정 조회/생성/수정 |
| 일반 응답 | 범용 질의응답 및 업무 지원 |

### 1.3 개발 환경
- **패키지 관리**: uv
- **언어**: Python 3.11+
- **프레임워크**: Google ADK (Agent Development Kit)
- **데이터 검증**: Pydantic v2
- **향후 DB**: Vertex AI Search (GCP)
- **현재 DB**: Mock/In-memory (구조만 구성)

---

## 2. 시스템 아키텍처

### 2.1 전체 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  (Web UI / API Client / CLI)                                    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API Gateway (FastAPI)                        │
│  - Authentication                                                │
│  - Rate Limiting                                                 │
│  - Request Routing                                               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Orchestrator (Google ADK)                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Router Agent                          │    │
│  │  - Intent Classification                                 │    │
│  │  - Agent Selection                                       │    │
│  │  - Response Aggregation                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│    ┌──────────┬──────────┬──────────┬──────────┬──────────┐    │
│    ▼          ▼          ▼          ▼          ▼          │    │
│ ┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐       │    │
│ │Translat││ Email  ││Meeting ││Calendar││General │       │    │
│ │ Agent  ││ Agent  ││ Agent  ││ Agent  ││ Agent  │       │    │
│ └────────┘└────────┘└───┬────┘└───▲────┘└────────┘       │    │
│                         │         │                       │    │
│                         └─────────┘                       │    │
│                     (회의 예약 연동)                        │    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Vertex AI    │  │   Cache      │  │   Logging    │          │
│  │ Search (TBD) │  │  (Memory)    │  │   Storage    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 에이전트 오케스트레이션 흐름

```
사용자 요청
    │
    ▼
[Router Agent] ─── Intent 분류
    │
    ├─── "번역해줘" ──────────► [Translation Agent]
    │
    ├─── "메일 요약/회신" ────► [Email Agent] ──┐
    │                                          │ (일정 추출 시)
    ├─── "회의록 정리" ───────► [Meeting Agent]─┼──► [Calendar Agent]
    │                                          │ (회의 예약 시)
    ├─── "일정 확인/등록" ────► [Calendar Agent]◄──┘
    │
    └─── 기타 ────────────────► [General Agent]
    │
    ▼
응답 생성 및 반환
```

---

## 3. 에이전트 상세 명세

### 3.1 Router Agent (라우터 에이전트)

**역할**: 사용자 의도 파악 및 적절한 에이전트로 라우팅

```python
class RouterInput(BaseModel):
    """라우터 입력 스키마"""
    user_message: str
    context: Optional[dict] = None
    session_id: str

class RouterOutput(BaseModel):
    """라우터 출력 스키마"""
    intent: Literal["translation", "email", "meeting", "calendar", "general"]
    confidence: float
    routed_agent: str
    preprocessed_input: dict
```

**Intent 분류 기준**:
| Intent | 트리거 키워드/패턴 |
|--------|-------------------|
| translation | 번역, translate, 통역, ~어로, ~語로 |
| email | 메일, 이메일, email, 회신, 답장, 요약 + 메일 |
| meeting | 회의록, 회의 내용, 미팅 노트, 정리, 요약 + 회의 |
| calendar | 일정, 스케줄, 캘린더, 약속, 예약, 언제, 오늘/내일/이번주 + 일정 |
| general | 위 패턴에 해당하지 않는 모든 요청 |

---

### 3.2 Translation Agent (통번역 에이전트)

**역할**: 다국어 번역 및 통역 지원

```python
class TranslationInput(BaseModel):
    """번역 입력 스키마"""
    text: str
    source_language: Optional[str] = "auto"  # 자동 감지
    target_language: str
    style: Literal["formal", "casual", "business"] = "business"
    domain: Optional[str] = None  # IT, 법률, 의료 등

class TranslationOutput(BaseModel):
    """번역 출력 스키마"""
    original_text: str
    translated_text: str
    detected_language: str
    target_language: str
    confidence: float
    alternatives: Optional[List[str]] = None
```

**지원 언어**:
- 한국어 (ko)
- 영어 (en)
- 일본어 (ja)
- 중국어 간체 (zh-CN)
- 중국어 번체 (zh-TW)

**기능 상세**:
1. 자동 언어 감지
2. 비즈니스 문서 특화 번역
3. 전문 용어 사전 지원 (확장 가능)
4. 번역 스타일 선택 (격식체/비격식체/비즈니스)

---

### 3.3 Email Agent (메일 에이전트)

**역할**: 이메일 요약 및 회신 초안 생성

```python
class EmailInput(BaseModel):
    """메일 입력 스키마"""
    email_content: str
    action: Literal["summarize", "reply", "both"] = "both"
    reply_tone: Literal["formal", "friendly", "concise"] = "formal"
    additional_context: Optional[str] = None
    include_original: bool = False

class EmailSummary(BaseModel):
    """메일 요약 스키마"""
    subject_summary: str
    key_points: List[str]
    action_items: List[str]
    sentiment: Literal["positive", "neutral", "negative", "urgent"]
    priority: Literal["high", "medium", "low"]

class EmailReply(BaseModel):
    """메일 회신 스키마"""
    subject: str
    body: str
    tone: str

class EmailOutput(BaseModel):
    """메일 출력 스키마"""
    summary: Optional[EmailSummary] = None
    reply_draft: Optional[EmailReply] = None
    processing_time: float
```

**기능 상세**:
1. 메일 핵심 내용 요약 (3-5개 포인트)
2. Action Item 자동 추출
3. 긴급도/중요도 판단
4. 톤에 맞는 회신 초안 생성
5. 다국어 메일 지원 (번역 에이전트 연동)

---

### 3.4 Meeting Agent (회의록 에이전트)

**역할**: 회의 내용 요약 및 정리

```python
class MeetingInput(BaseModel):
    """회의록 입력 스키마"""
    content: str  # 회의 녹취록 또는 메모
    meeting_type: Literal["standup", "planning", "review", "general"] = "general"
    participants: Optional[List[str]] = None
    format: Literal["bullet", "narrative", "structured"] = "structured"

class ActionItem(BaseModel):
    """액션 아이템 스키마"""
    task: str
    assignee: Optional[str] = None
    due_date: Optional[str] = None
    priority: Literal["high", "medium", "low"] = "medium"

class Decision(BaseModel):
    """결정 사항 스키마"""
    topic: str
    decision: str
    rationale: Optional[str] = None

class MeetingOutput(BaseModel):
    """회의록 출력 스키마"""
    title: str
    date: str
    participants: List[str]
    summary: str
    key_discussions: List[str]
    decisions: List[Decision]
    action_items: List[ActionItem]
    next_steps: List[str]
    raw_notes: Optional[str] = None
```

**기능 상세**:
1. 회의 유형별 템플릿 지원
2. 핵심 논의 사항 추출
3. 결정 사항 명시
4. Action Item + 담당자 + 기한 자동 추출
5. 후속 조치 사항 정리

---

### 3.5 Calendar Agent (캘린더 에이전트)

**역할**: Google Calendar MCP를 활용한 일정 관리

**MCP 연동**: `google-calendar-mcp`

```python
class CalendarInput(BaseModel):
    """캘린더 입력 스키마"""
    action: Literal["query", "create", "update", "delete"]
    query: Optional[str] = None  # 자연어 쿼리
    event: Optional["CalendarEvent"] = None
    date_range: Optional["DateRange"] = None

class DateRange(BaseModel):
    """날짜 범위"""
    start: datetime
    end: datetime

class CalendarEvent(BaseModel):
    """캘린더 이벤트"""
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    reminder_minutes: int = 30

class CalendarOutput(BaseModel):
    """캘린더 출력 스키마"""
    action_performed: str
    events: Optional[List[CalendarEvent]] = None
    created_event: Optional[CalendarEvent] = None
    message: str
    success: bool
```

**기능 상세**:
1. **일정 조회**: 오늘/이번주/특정 기간 일정 조회
2. **일정 생성**: 자연어로 일정 생성 ("내일 오후 2시에 팀 미팅 잡아줘")
3. **일정 수정**: 기존 일정 시간/장소/참석자 변경
4. **일정 삭제**: 일정 취소
5. **에이전트 간 연동**:
   - Meeting Agent → 회의 예약 시 Calendar Agent 호출
   - Email Agent → Action Item에서 날짜 추출 시 Calendar Agent 호출

**MCP 도구 사용**:
```python
# Google Calendar MCP 도구 목록
CALENDAR_TOOLS = [
    "list_events",      # 이벤트 목록 조회
    "get_event",        # 특정 이벤트 조회
    "create_event",     # 이벤트 생성
    "update_event",     # 이벤트 수정
    "delete_event",     # 이벤트 삭제
    "list_calendars",   # 캘린더 목록 조회
]
```

---

### 3.6 General Agent (일반 응답 에이전트)

**역할**: 범용 질의응답 및 업무 지원

```python
class GeneralInput(BaseModel):
    """일반 입력 스키마"""
    query: str
    context: Optional[str] = None
    response_format: Literal["text", "markdown", "json"] = "markdown"
    max_length: Optional[int] = None

class GeneralOutput(BaseModel):
    """일반 출력 스키마"""
    response: str
    format: str
    sources: Optional[List[str]] = None
    follow_up_suggestions: Optional[List[str]] = None
```

**기능 상세**:
1. 일반 질의응답
2. 문서 작성 지원
3. 아이디어 브레인스토밍
4. 업무 조언 및 가이드
5. 다른 에이전트로 라우팅 제안

---

## 4. API 설계

### 4.1 엔드포인트 목록

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/chat` | 통합 채팅 엔드포인트 (오케스트레이터 사용) |
| POST | `/api/v1/translate` | 번역 직접 호출 |
| POST | `/api/v1/email/process` | 메일 처리 직접 호출 |
| POST | `/api/v1/meeting/summarize` | 회의록 요약 직접 호출 |
| POST | `/api/v1/general` | 일반 응답 직접 호출 |
| POST | `/api/v1/calendar/events` | 캘린더 이벤트 생성 |
| GET | `/api/v1/calendar/events` | 캘린더 이벤트 목록 조회 |
| PUT | `/api/v1/calendar/events/{id}` | 캘린더 이벤트 수정 |
| DELETE | `/api/v1/calendar/events/{id}` | 캘린더 이벤트 삭제 |
| GET | `/api/v1/health` | 헬스체크 |
| GET | `/api/v1/agents/status` | 에이전트 상태 조회 |

### 4.2 통합 채팅 API

```python
# Request
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: str
    metadata: Optional[dict] = None

# Response
class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    agent_used: str
    response: Union[
        TranslationOutput,
        EmailOutput,
        MeetingOutput,
        CalendarOutput,
        GeneralOutput
    ]
    timestamp: datetime
    processing_time_ms: int
```

### 4.3 에러 응답 형식

```python
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime

# 에러 코드
ERROR_CODES = {
    "E001": "Invalid input format",
    "E002": "Agent not available",
    "E003": "Rate limit exceeded",
    "E004": "Authentication failed",
    "E005": "Internal server error",
}
```

---

## 5. 데이터 모델

### 5.1 세션 관리

```python
class Session(BaseModel):
    """세션 모델"""
    session_id: str
    user_id: str
    created_at: datetime
    last_active: datetime
    context: dict = {}
    history: List[dict] = []

class ConversationTurn(BaseModel):
    """대화 턴 모델"""
    turn_id: str
    session_id: str
    user_input: str
    agent_response: dict
    agent_used: str
    timestamp: datetime
    feedback: Optional[Literal["positive", "negative"]] = None
```

### 5.2 향후 Vertex AI Search 연동 구조 (Mock)

```python
class DocumentStore(ABC):
    """문서 저장소 추상 클래스"""

    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> List[Document]:
        pass

    @abstractmethod
    async def add_document(self, document: Document) -> str:
        pass

class MockDocumentStore(DocumentStore):
    """개발용 Mock 저장소"""
    pass

class VertexAISearchStore(DocumentStore):
    """Vertex AI Search 구현 (향후)"""
    pass
```

---

## 6. 프론트엔드 (React + Vite)

### 6.1 UI 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                         Header                                   │
│  [Logo]                                    [Settings] [User]    │
├─────────────────────────────────────────────────────────────────┤
│  Sidebar          │              Main Content                    │
│  ┌─────────────┐  │  ┌─────────────────────────────────────┐    │
│  │ 💬 채팅      │  │  │                                     │    │
│  │ 🌐 통번역    │  │  │         Chat Interface              │    │
│  │ 📧 메일     │  │  │                                     │    │
│  │ 📝 회의록   │  │  │    [대화 히스토리 표시 영역]         │    │
│  │ 💡 일반     │  │  │                                     │    │
│  └─────────────┘  │  │                                     │    │
│                   │  ├─────────────────────────────────────┤    │
│  History          │  │  [입력창]              [전송 버튼]   │    │
│  ┌─────────────┐  │  └─────────────────────────────────────┘    │
│  │ 최근 대화1  │  │                                              │
│  │ 최근 대화2  │  │                                              │
│  │ ...        │  │                                              │
│  └─────────────┘  │                                              │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 주요 컴포넌트

```typescript
// 컴포넌트 구조
src/
├── components/
│   ├── chat/
│   │   ├── ChatWindow.tsx       // 채팅 메인 윈도우
│   │   ├── MessageList.tsx      // 메시지 목록
│   │   ├── MessageItem.tsx      // 개별 메시지
│   │   ├── InputArea.tsx        // 입력 영역
│   │   └── AgentIndicator.tsx   // 사용된 에이전트 표시
│   │
│   ├── sidebar/
│   │   ├── Sidebar.tsx          // 사이드바
│   │   ├── AgentSelector.tsx    // 에이전트 선택
│   │   └── History.tsx          // 대화 히스토리
│   │
│   ├── agents/
│   │   ├── TranslationPanel.tsx // 번역 전용 패널
│   │   ├── EmailPanel.tsx       // 메일 전용 패널
│   │   └── MeetingPanel.tsx     // 회의록 전용 패널
│   │
│   └── common/
│       ├── Header.tsx
│       ├── Button.tsx
│       ├── Input.tsx
│       └── Modal.tsx
```

### 6.3 상태 관리

```typescript
// Zustand Store 구조
interface AppState {
  // 세션
  sessionId: string | null;

  // 채팅
  messages: Message[];
  isLoading: boolean;

  // 에이전트
  currentAgent: AgentType;
  agentStatus: Record<AgentType, 'ready' | 'busy' | 'error'>;

  // 액션
  sendMessage: (content: string) => Promise<void>;
  selectAgent: (agent: AgentType) => void;
  clearHistory: () => void;
}

type AgentType = 'auto' | 'translation' | 'email' | 'meeting' | 'calendar' | 'general';
```

### 6.4 기술 스택 (Frontend)

| 구분 | 기술 |
|------|------|
| Framework | React 18 |
| Build Tool | Vite |
| Language | TypeScript |
| Styling | Tailwind CSS |
| State | Zustand |
| HTTP Client | Axios / TanStack Query |
| Routing | React Router v6 |
| UI Components | shadcn/ui |

---

## 7. 프로젝트 구조

```
aiok/
├── pyproject.toml
├── README.md
├── .env.example
├── .gitignore
│
├── ui/                             # React Frontend
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── components/
│       ├── hooks/
│       ├── stores/
│       ├── services/
│       ├── types/
│       └── styles/
│
├── src/
│   └── aiok/
│       ├── __init__.py
│       ├── main.py                 # FastAPI 앱 엔트리포인트
│       ├── config.py               # 설정 관리
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   ├── router.py           # API 라우터
│       │   ├── dependencies.py     # 의존성 주입
│       │   └── middleware.py       # 미들웨어
│       │
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base.py             # 베이스 에이전트
│       │   ├── orchestrator.py     # 오케스트레이터
│       │   ├── router_agent.py     # 라우터 에이전트
│       │   ├── translation.py      # 통번역 에이전트
│       │   ├── email.py            # 메일 에이전트
│       │   ├── meeting.py          # 회의록 에이전트
│       │   ├── calendar.py         # 캘린더 에이전트 (Google Calendar MCP)
│       │   └── general.py          # 일반 에이전트
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── requests.py         # 요청 모델
│       │   ├── responses.py        # 응답 모델
│       │   └── entities.py         # 도메인 엔티티
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── session.py          # 세션 관리
│       │   └── storage.py          # 저장소 서비스
│       │
│       └── utils/
│           ├── __init__.py
│           ├── logger.py           # 로깅
│           └── helpers.py          # 유틸리티 함수
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_agents/
│   ├── test_api/
│   └── test_services/
│
└── docs/
    ├── DEVELOPMENT_SPEC.md         # 본 문서
    ├── API_REFERENCE.md
    └── DEPLOYMENT_GUIDE.md
```

---

## 7. 개발 단계

### Phase 1: 기반 구축 (Foundation)
- [ ] 프로젝트 초기 설정 (uv, pyproject.toml)
- [ ] 기본 디렉토리 구조 생성
- [ ] Pydantic 모델 정의
- [ ] FastAPI 기본 설정
- [ ] 로깅 시스템 구축

### Phase 2: 에이전트 개발 (Agent Development)
- [ ] Base Agent 클래스 구현
- [ ] Router Agent 구현
- [ ] Translation Agent 구현
- [ ] Email Agent 구현
- [ ] Meeting Agent 구현
- [ ] Calendar Agent 구현 (Google Calendar MCP 연동)
- [ ] General Agent 구현

### Phase 3: 오케스트레이션 (Orchestration)
- [ ] Google ADK 연동
- [ ] 오케스트레이터 구현
- [ ] 에이전트 간 통신 구현
- [ ] 세션 관리 구현

### Phase 4: API 개발 (API Layer)
- [ ] REST API 엔드포인트 구현
- [ ] 인증/인가 구현
- [ ] Rate Limiting 구현
- [ ] API 문서화 (OpenAPI)

### Phase 5: 프론트엔드 개발 (Frontend)
- [ ] React + Vite 프로젝트 초기 설정
- [ ] 공통 컴포넌트 개발
- [ ] 채팅 인터페이스 구현
- [ ] 에이전트별 전용 패널 구현
- [ ] API 연동
- [ ] 반응형 디자인 적용

### Phase 6: 테스트 및 QA (Testing & QA)
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 작성
- [ ] E2E 테스트 작성 (Playwright)
- [ ] 성능 테스트

### Phase 7: 상용화 준비 (Production Ready)
- [ ] Vertex AI Search 연동
- [ ] GCP 배포 설정
- [ ] 모니터링 설정
- [ ] 문서화 완료

---

## 8. 기술 스택 요약

### Backend
| 구분 | 기술 |
|------|------|
| Language | Python 3.11+ |
| Package Manager | uv |
| Web Framework | FastAPI |
| Agent Framework | Google ADK |
| Data Validation | Pydantic v2 |
| Testing | pytest, pytest-asyncio |
| Linting | ruff, black |
| Type Checking | mypy |
| Future DB | Vertex AI Search |
| Cloud | GCP |

### Frontend
| 구분 | 기술 |
|------|------|
| Language | TypeScript |
| Framework | React 18 |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| State Management | Zustand |
| HTTP Client | TanStack Query + Axios |
| UI Components | shadcn/ui |
| Testing | Vitest, Playwright |

---

## 9. 비기능 요구사항

### 9.1 성능
- API 응답 시간: 일반 요청 < 3초, 복잡 요청 < 10초
- 동시 사용자: 초기 50명, 확장 가능 설계

### 9.2 보안
- API Key 기반 인증
- 입력 데이터 검증 및 sanitization
- 민감 정보 로깅 제외

### 9.3 가용성
- 99.5% uptime 목표
- Graceful degradation (에이전트 장애 시 General로 폴백)

### 9.4 확장성
- 새 에이전트 추가 용이한 플러그인 구조
- 수평 확장 가능한 설계

---

## 10. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|----------|
| 1.0.0 | 2026-03-23 | AI | 초안 작성 |

