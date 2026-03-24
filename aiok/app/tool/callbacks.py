"""Tool callbacks for agents."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def before_tool_callback(tool: Any, args: dict, tool_context: Any) -> None:
    """도구 실행 전 로깅 콜백."""
    tool_name = getattr(tool, 'name', str(tool))
    logger.info(f"[Tool] {tool_name} called with: {args}")


def tool_callbacks() -> dict[str, object]:
    """에이전트에 전달할 콜백 딕셔너리."""
    return {
        "before_tool_callback": before_tool_callback,
    }
