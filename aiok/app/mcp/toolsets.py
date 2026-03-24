"""MCP Toolset definitions."""

from __future__ import annotations

import os

from mcp import StdioServerParameters

from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams

from app.config.settings import settings


# Google Calendar MCP Toolset
calendar_toolset: MCPToolset | None = None

if settings.enable_calendar_mcp:
    calendar_toolset = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@anthropic-ai/google-calendar-mcp"],
            ),
            timeout=10.0,
        ),
        tool_name_prefix="calendar_",
    )
    print("Calendar MCP enabled")


# GitHub MCP Toolset
github_toolset: MCPToolset | None = None

if settings.enable_github_mcp and settings.github_token:
    github_toolset = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"],
                env={
                    **os.environ,
                    "GITHUB_PERSONAL_ACCESS_TOKEN": settings.github_token,
                },
            ),
            timeout=15.0,
        ),
        tool_name_prefix="github_",
    )
    print(f"GitHub MCP enabled (repo: {settings.github_repo})")


# Notion MCP Toolset
notion_toolset: MCPToolset | None = None

if settings.enable_notion_mcp and settings.notion_token:
    notion_toolset = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@notionhq/notion-mcp-server"],
                env={
                    **os.environ,
                    "NOTION_TOKEN": settings.notion_token,
                },
            ),
            timeout=15.0,
        ),
        tool_name_prefix="notion_",
    )
    print("Notion MCP enabled")
