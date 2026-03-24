"""Root agent definition - Supervisor pattern."""

from __future__ import annotations

from google.adk.agents import Agent

from app.agent.workflows import pr_review_workflow, release_notes_workflow
from app.config.settings import settings
from app.mcp.toolsets import calendar_toolset
from app.prompt.instructions import AGENT_DESCRIPTION, AIOK_SYSTEM_INSTRUCTION
from app.tool import generate_reply, summarize_email, summarize_meeting, translate_text


root_agent = Agent(
    name="aiok",
    model=settings.model,
    description=AGENT_DESCRIPTION,
    instruction=AIOK_SYSTEM_INSTRUCTION,
    tools=[
        translate_text,
        summarize_email,
        generate_reply,
        summarize_meeting,
        calendar_toolset,
    ] if calendar_toolset else [
        translate_text,
        summarize_email,
        generate_reply,
        summarize_meeting,
    ],
    sub_agents=[
        pr_review_workflow,
        release_notes_workflow,
    ],
)
