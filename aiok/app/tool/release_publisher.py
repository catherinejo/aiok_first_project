"""Release publishing tools (GitHub Release, comments, changelog commit/push)."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from urllib import error, request

from google.adk.tools.tool_context import ToolContext

from app.config.settings import settings


def _run_git(command: list[str], cwd: Path) -> tuple[bool, str]:
    """Run git command and return success/output."""
    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - defensive
        return False, str(exc)

    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout).strip()
    return True, (proc.stdout or "").strip()


def _github_api(method: str, path: str, payload: dict) -> dict:
    """Call GitHub REST API with configured token."""
    if not settings.github_token:
        return {"ok": False, "error": "GITHUB_TOKEN is not configured"}

    url = f"https://api.github.com{path}"
    req = request.Request(
        url=url,
        method=method,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            return {"ok": True, "data": json.loads(body)}
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        return {"ok": False, "error": f"HTTP {exc.code}: {detail}"}
    except Exception as exc:  # pragma: no cover - defensive
        return {"ok": False, "error": str(exc)}


def _notion_api(method: str, path: str, payload: dict) -> dict:
    """Call Notion REST API with configured token."""
    if not settings.notion_token:
        return {"ok": False, "error": "NOTION_TOKEN is not configured"}

    url = f"https://api.notion.com{path}"
    req = request.Request(
        url=url,
        method=method,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.notion_token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8")
            return {"ok": True, "data": json.loads(body)}
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        return {"ok": False, "error": f"HTTP {exc.code}: {detail}"}
    except Exception as exc:  # pragma: no cover - defensive
        return {"ok": False, "error": str(exc)}


def save_release_notes_to_notion(
    release_tag: str,
    release_notes_ko: str,
    release_notes_en: str,
    page_id: str = "",
    tool_context: ToolContext | None = None,
) -> str:
    """Create a Notion child page and save release notes."""
    parent_page_id = page_id or (settings.notion_page_id or "")
    if not parent_page_id:
        return json.dumps({"ok": False, "error": "NOTION_PAGE_ID is required"}, ensure_ascii=False)

    title = f"Release {release_tag}"
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "properties": {
            "title": {
                "title": [
                    {"type": "text", "text": {"content": title}},
                ]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Korean"}}]},
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": release_notes_ko[:1900]}}]},
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "English"}}]},
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": release_notes_en[:1900]}}]},
            },
        ],
    }
    res = _notion_api("POST", "/v1/pages", payload)
    if res.get("ok"):
        data = res["data"]
        result = {
            "ok": True,
            "page_id": data.get("id"),
            "url": data.get("url"),
            "title": title,
        }
    else:
        result = {"ok": False, "error": res.get("error", "unknown error")}

    if tool_context:
        tool_context.state["notion_publish_result"] = result
    return json.dumps(result, ensure_ascii=False, indent=2)


def publish_release_bundle(
    release_tag: str,
    release_title: str,
    release_notes_ko: str,
    release_notes_en: str,
    comment_targets: str = "",
    classified_changes: str = "",
    tool_context: ToolContext | None = None,
) -> str:
    """Publish release artifacts to GitHub and changelog.

    Args:
        release_tag: Release tag (e.g., v1.2.0)
        release_title: Release title
        release_notes_ko: Korean release notes
        release_notes_en: English release notes
        comment_targets: Comma-separated issue/pr numbers (e.g., "12,45")
        classified_changes: Raw classified text for auto target extraction
        tool_context: ADK tool context
    """
    repo = settings.github_repo
    if "/" not in repo:
        return json.dumps({"ok": False, "error": "Invalid GITHUB_REPO"}, ensure_ascii=False)

    project_root = Path(__file__).resolve().parents[2]
    changelog_path = project_root / "CHANGELOG.md"
    now = datetime.now().strftime("%Y-%m-%d")

    notes = f"## 🇰🇷 한국어\n\n{release_notes_ko}\n\n---\n\n## 🇺🇸 English\n\n{release_notes_en}\n"

    # 1) Update CHANGELOG.md
    existing = changelog_path.read_text(encoding="utf-8") if changelog_path.exists() else "# Changelog\n\n"
    entry = f"## {release_tag} - {now}\n\n{notes}\n"
    if entry not in existing:
        if existing.startswith("# Changelog"):
            new_content = existing.rstrip() + "\n\n" + entry
        else:
            new_content = "# Changelog\n\n" + existing.rstrip() + "\n\n" + entry
        changelog_path.write_text(new_content, encoding="utf-8")

    # 2) Commit + Push changelog
    commit_result = {"ok": True, "message": "skipped"}
    ok, out = _run_git(["git", "add", "CHANGELOG.md"], project_root)
    if ok:
        ok, status = _run_git(["git", "status", "--porcelain"], project_root)
        if ok and status:
            ok, out = _run_git(
                ["git", "commit", "-m", f"docs: update changelog for {release_tag}"],
                project_root,
            )
            if ok:
                ok, out = _run_git(["git", "push", "origin", "HEAD"], project_root)
                commit_result = {"ok": ok, "message": out}
            else:
                commit_result = {"ok": False, "message": out}
        else:
            commit_result = {"ok": True, "message": "no changes to commit"}
    else:
        commit_result = {"ok": False, "message": out}

    # 3) Create GitHub Release
    release_payload = {
        "tag_name": release_tag,
        "name": release_title,
        "body": notes,
        "draft": False,
        "prerelease": False,
    }
    release_res = _github_api("POST", f"/repos/{repo}/releases", release_payload)
    release_url = ""
    if release_res.get("ok"):
        release_url = release_res["data"].get("html_url", "")

    # 4) Add comments to PR/Issue targets
    comments: list[dict] = []
    body = f"🚀 `{release_tag}` 배포 노트가 등록되었습니다.\n\n{release_url}".strip()
    targets = [t.strip() for t in comment_targets.split(",") if t.strip()]
    if not targets and classified_changes:
        # Auto-extract #123 style references from classification output.
        targets = sorted(set(re.findall(r"#(\d+)", classified_changes)))
    for target in targets:
        if not target.isdigit():
            comments.append({"target": target, "ok": False, "error": "invalid target"})
            continue
        res = _github_api(
            "POST",
            f"/repos/{repo}/issues/{target}/comments",
            {"body": body},
        )
        comments.append({"target": target, "ok": res.get("ok"), "detail": res.get("error", "")})

    result = {
        "ok": True,
        "repo": repo,
        "release_tag": release_tag,
        "release_url": release_url,
        "changelog_commit_push": commit_result,
        "comments": comments,
    }

    if tool_context:
        tool_context.state["release_publish_result"] = result

    return json.dumps(result, ensure_ascii=False, indent=2)
