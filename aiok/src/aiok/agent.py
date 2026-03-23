"""AIOK Agent - Google ADK 기반 업무자동화 AI 에이전트."""

from google.adk import Agent

from aiok.config import get_settings
from aiok.tools.email import generate_reply, summarize_email
from aiok.tools.meeting import summarize_meeting
from aiok.tools.translation import translate_text

# 기본 도구 목록
tools = [
    translate_text,
    summarize_email,
    generate_reply,
    summarize_meeting,
]

# Google Calendar MCP Toolset (설정된 경우에만 추가)
# .env에서 ENABLE_CALENDAR_MCP=true 로 활성화
settings = get_settings()
if settings.enable_calendar_mcp:
    from google.adk.tools import McpToolset
    from google.adk.tools.mcp_tool.mcp_toolset import StdioConnectionParams
    from mcp.client.stdio import StdioServerParameters

    calendar_mcp = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@anthropic-ai/google-calendar-mcp"],
            ),
            timeout=10.0,
        ),
        tool_name_prefix="calendar_",
    )
    tools.append(calendar_mcp)
    print("Calendar MCP enabled")

# 메인 에이전트 정의
aiok_agent = Agent(
    name="aiok",
    model="gemini-2.0-flash",
    description="업무자동화 AI 에이전트 - 통번역, 메일, 회의록, 일정 관리 지원",
    instruction="""
당신은 회사 업무를 자동화하는 AI 어시스턴트 'AIOK'입니다.

## 핵심 기능
1. **통번역**: 다국어 번역 지원 (한/영/일/중)
2. **메일 처리**: 메일 요약 및 회신 초안 생성
3. **회의록 정리**: 회의 내용 요약, 액션 아이템 추출
4. **일정 관리**: Google Calendar MCP (별도 설정 필요)

## 응답 원칙
- 한국어로 응답합니다
- 명확하고 간결하게 답변합니다
- 필요한 경우 적절한 도구를 사용합니다

## 도구 사용
- 번역 → translate_text
- 메일 요약 → summarize_email
- 메일 회신 → generate_reply
- 회의록 → summarize_meeting
""",
    tools=tools,
)
