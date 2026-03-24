"""Agent workflows using Sequential and Parallel agents."""

from __future__ import annotations

from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.sequential_agent import SequentialAgent

from app.agent.sub_agents import (
    make_classifier_agent,
    make_issue_linker_agent,
    make_pr_analyzer_agent,
    make_pr_collector_agent,
    make_pr_fetcher_agent,
    make_pr_reviewer_agent,
    make_release_writer_agent,
)


# =============================================================================
# PR Review Workflow (Sequential)
# =============================================================================
# fetcher → analyzer → reviewer

pr_review_workflow = SequentialAgent(
    name="pr_review_workflow",
    sub_agents=[
        make_pr_fetcher_agent(),
        make_pr_analyzer_agent(),
        make_pr_reviewer_agent(),
    ],
    description="PR을 분석하고 리뷰 포인트를 생성한다.",
)


# =============================================================================
# Release Notes Workflow (Parallel + Sequential)
# =============================================================================
# [parallel: pr_collector, issue_linker] → classifier → writer

parallel_collect_agent = ParallelAgent(
    name="ParallelCollectAgent",
    sub_agents=[
        make_pr_collector_agent(),
        make_issue_linker_agent(),
    ],
    description="PR과 이슈를 병렬로 수집한다.",
)

release_notes_workflow = SequentialAgent(
    name="release_notes_workflow",
    sub_agents=[
        parallel_collect_agent,
        make_classifier_agent(),
        make_release_writer_agent(),
    ],
    description="릴리즈 노트를 자동 생성한다.",
)
