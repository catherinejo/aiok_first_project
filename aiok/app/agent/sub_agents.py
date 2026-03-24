"""Sub-agent factory functions."""

from __future__ import annotations

from google.adk.agents.llm_agent import LlmAgent

from app.config.settings import settings
from app.mcp.toolsets import github_toolset
from app.prompt.instructions import (
    CLASSIFIER_INSTRUCTION,
    COMMIT_COLLECTOR_INSTRUCTION,
    ISSUE_LINKER_INSTRUCTION,
    NOTION_PUBLISHER_INSTRUCTION,
    PR_ANALYZER_INSTRUCTION,
    PR_COLLECTOR_INSTRUCTION,
    PR_FETCHER_INSTRUCTION,
    PR_REVIEWER_INSTRUCTION,
    RELEASE_PUBLISHER_INSTRUCTION,
    RELEASE_TRANSLATOR_INSTRUCTION,
    RELEASE_WRITER_INSTRUCTION,
)
from app.tool import publish_release_bundle, save_release_notes_to_notion
from app.tool.callbacks import tool_callbacks


# =============================================================================
# PR Review Agents
# =============================================================================

def make_pr_fetcher_agent() -> LlmAgent:
    """PR 정보 수집 에이전트."""
    return LlmAgent(
        name="PRFetcherAgent",
        model=settings.model,
        instruction=PR_FETCHER_INSTRUCTION.format(default_repo=settings.github_repo),
        tools=[github_toolset] if github_toolset else [],
        output_key="pr_info",
        **tool_callbacks(),
    )


def make_pr_analyzer_agent() -> LlmAgent:
    """PR 코드 분석 에이전트."""
    return LlmAgent(
        name="PRAnalyzerAgent",
        model=settings.model,
        instruction=PR_ANALYZER_INSTRUCTION,
        output_key="pr_analysis",
        **tool_callbacks(),
    )


def make_pr_reviewer_agent() -> LlmAgent:
    """PR 리뷰 포인트 생성 에이전트."""
    return LlmAgent(
        name="PRReviewerAgent",
        model=settings.model,
        instruction=PR_REVIEWER_INSTRUCTION,
        output_key="pr_review_result",
        **tool_callbacks(),
    )


# =============================================================================
# Release Notes Agents
# =============================================================================

def make_pr_collector_agent() -> LlmAgent:
    """머지된 PR 수집 에이전트."""
    return LlmAgent(
        name="PRCollectorAgent",
        model=settings.model,
        instruction=PR_COLLECTOR_INSTRUCTION.format(default_repo=settings.github_repo),
        tools=[github_toolset] if github_toolset else [],
        output_key="collected_prs",
        **tool_callbacks(),
    )


def make_issue_linker_agent() -> LlmAgent:
    """이슈 연결 에이전트."""
    return LlmAgent(
        name="IssueLinkerAgent",
        model=settings.model,
        instruction=ISSUE_LINKER_INSTRUCTION.format(default_repo=settings.github_repo),
        tools=[github_toolset] if github_toolset else [],
        output_key="linked_issues",
        **tool_callbacks(),
    )


def make_classifier_agent() -> LlmAgent:
    """변경사항 분류 에이전트."""
    return LlmAgent(
        name="ClassifierAgent",
        model=settings.model,
        instruction=CLASSIFIER_INSTRUCTION,
        output_key="classified_changes",
        **tool_callbacks(),
    )


def make_commit_collector_agent() -> LlmAgent:
    """커밋 히스토리 수집 에이전트."""
    return LlmAgent(
        name="CommitCollectorAgent",
        model=settings.model,
        instruction=COMMIT_COLLECTOR_INSTRUCTION.format(default_repo=settings.github_repo),
        tools=[github_toolset] if github_toolset else [],
        output_key="collected_commits",
        **tool_callbacks(),
    )


def make_release_writer_agent() -> LlmAgent:
    """릴리즈 노트 작성 에이전트."""
    return LlmAgent(
        name="ReleaseWriterAgent",
        model=settings.model,
        instruction=RELEASE_WRITER_INSTRUCTION,
        output_key="release_notes",
        **tool_callbacks(),
    )


def make_release_translator_agent() -> LlmAgent:
    """릴리즈 노트 번역 에이전트."""
    return LlmAgent(
        name="ReleaseTranslatorAgent",
        model=settings.model,
        instruction=RELEASE_TRANSLATOR_INSTRUCTION,
        output_key="release_notes_en",
        **tool_callbacks(),
    )


def make_notion_publisher_agent() -> LlmAgent:
    """릴리즈 노트 Notion 저장 에이전트."""
    from app.mcp.toolsets import notion_toolset

    instruction = NOTION_PUBLISHER_INSTRUCTION
    instruction = instruction.replace("{default_repo}", settings.github_repo)
    instruction = instruction.replace("{notion_page_id}", settings.notion_page_id or "")

    return LlmAgent(
        name="NotionPublisherAgent",
        model=settings.model,
        instruction=instruction,
        tools=([notion_toolset] if notion_toolset else []) + [save_release_notes_to_notion],
        output_key="notion_publish_result",
        **tool_callbacks(),
    )


def make_release_publisher_agent() -> LlmAgent:
    """릴리즈 노트 GitHub 게시 에이전트."""
    return LlmAgent(
        name="ReleasePublisherAgent",
        model=settings.model,
        instruction=RELEASE_PUBLISHER_INSTRUCTION,
        tools=[publish_release_bundle],
        output_key="release_publish_result",
        **tool_callbacks(),
    )
