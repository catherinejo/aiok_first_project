"""Email processing tools."""

from __future__ import annotations

from google.adk.tools.tool_context import ToolContext

from app.prompt.instructions import EMAIL_REPLY_INSTRUCTION, EMAIL_SUMMARIZE_INSTRUCTION


def summarize_email(
    email_content: str,
    tool_context: ToolContext | None = None,
) -> str:
    """이메일 내용을 요약합니다.

    Args:
        email_content: 요약할 이메일 전문
        tool_context: ADK tool context (optional)

    Returns:
        요약 지시사항
    """
    if tool_context:
        if "email_actions" not in tool_context.state:
            tool_context.state["email_actions"] = []
        tool_context.state["email_actions"].append("summarize")

    return f"[이메일 요약 요청]\n{email_content}\n\n{EMAIL_SUMMARIZE_INSTRUCTION}"


def generate_reply(
    email_content: str,
    tone: str = "formal",
    key_points: str | None = None,
    tool_context: ToolContext | None = None,
) -> str:
    """이메일 회신 초안을 생성합니다.

    Args:
        email_content: 원본 이메일 내용
        tone: 회신 톤 (formal, friendly, concise)
        key_points: 회신에 포함할 핵심 내용 (선택)
        tool_context: ADK tool context (optional)

    Returns:
        회신 생성 지시사항
    """
    if tool_context:
        if "email_actions" not in tool_context.state:
            tool_context.state["email_actions"] = []
        tool_context.state["email_actions"].append(f"reply_{tone}")

    instruction = EMAIL_REPLY_INSTRUCTION.format(tone=tone)
    result = f"[이메일 회신 요청]\n원본: {email_content}\n\n{instruction}"
    if key_points:
        result += f"\n\n포함할 내용: {key_points}"
    return result
