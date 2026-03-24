"""Translation tools."""

from __future__ import annotations

from google.adk.tools.tool_context import ToolContext

from app.prompt.instructions import TRANSLATION_INSTRUCTION


def translate_text(
    text: str,
    target_language: str,
    source_language: str = "auto",
    style: str = "business",
    tool_context: ToolContext | None = None,
) -> str:
    """텍스트를 다른 언어로 번역합니다.

    Args:
        text: 번역할 텍스트
        target_language: 목표 언어 (ko, en, ja, zh-CN, zh-TW)
        source_language: 원본 언어 (auto면 자동 감지)
        style: 번역 스타일 (formal, casual, business)
        tool_context: ADK tool context (optional)

    Returns:
        번역 지시사항
    """
    # Track translation requests in state
    if tool_context:
        if "translations" not in tool_context.state:
            tool_context.state["translations"] = []
        tool_context.state["translations"].append({
            "target": target_language,
            "style": style,
        })

    instruction = TRANSLATION_INSTRUCTION.format(
        target_language=target_language, style=style
    )
    return f"[번역 요청]\n원문: {text}\n\n{instruction}"
