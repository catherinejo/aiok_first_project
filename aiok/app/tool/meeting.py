"""Meeting processing tools."""

from __future__ import annotations

from google.adk.tools.tool_context import ToolContext

from app.prompt.instructions import (
    MEETING_ACTION_ITEMS_INSTRUCTION,
    MEETING_SUMMARIZE_INSTRUCTION,
)


def summarize_meeting(
    meeting_content: str,
    meeting_type: str = "general",
    extract_action_items: bool = True,
    tool_context: ToolContext | None = None,
) -> str:
    """회의 내용을 요약하고 정리합니다.

    Args:
        meeting_content: 회의 녹취록 또는 메모
        meeting_type: 회의 유형 (standup, planning, review, general)
        extract_action_items: 액션 아이템 추출 여부
        tool_context: ADK tool context (optional)

    Returns:
        회의 요약 지시사항
    """
    if tool_context:
        if "meetings" not in tool_context.state:
            tool_context.state["meetings"] = []
        tool_context.state["meetings"].append(meeting_type)

    instruction = MEETING_SUMMARIZE_INSTRUCTION.format(meeting_type=meeting_type)
    if extract_action_items:
        instruction += MEETING_ACTION_ITEMS_INSTRUCTION

    return f"[회의록 요약 요청]\n{meeting_content}\n\n{instruction}"
