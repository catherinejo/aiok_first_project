# Changelog

## v2026.03.24-test - 2026-03-24

## 🇰🇷 한국어

테스트 릴리즈 노트 KO

---

## 🇺🇸 English

Test release notes EN

## v2026.03.24-e2e4 - 2026-03-24

## 🇰🇷 한국어

## v2026.03.24-e2e4

*   **커밋 SHA:** bf46673c0ce405e659dc60db69d9452cc27040ed
    *   **작성자:** yhcho
    *   **커밋 메시지:** refactor: ADK 멀티에이전트 구조로 전환

        - src/aiok → app/ 구조로 변경 (ADK 권장 패턴)
        - Supervisor 패턴 적용 (root_agent가 의도 분석 후 라우팅)
        - PR 리뷰 워크플로우 추가 (Sequential: fetcher → analyzer → reviewer)
        - 릴리즈 노트 워크플로우 추가 (Parallel + Sequential)
        - GitHub MCP 연동 설정
        - UI: 세션 사이드바, 파일 첨부 기능 추가

        Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
*   **커밋 SHA:** 5813907634ce85fd99df63d4d656a17c1dbf00ec
    *   **작성자:** yhcho
    *   **커밋 메시지:** Initial commit: AIOK project setup

        - Python backend with FastAPI + LangChain agent
        - React + Vite frontend with chat interface
        - Google Calendar/Gmail integration tools
        - Project documentation

        Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

---

## 🇺🇸 English

## v2026.03.24-e2e4

*   **Commit SHA:** bf46673c0ce405e659dc60db69d9452cc27040ed
    *   **Author:** yhcho
    *   **Commit Message:** refactor: ADK 멀티에이전트 구조로 전환

        - src/aiok → app/ 구조로 변경 (ADK 권장 패턴)
        - Supervisor 패턴 적용 (root_agent가 의도 분석 후 라우팅)
        - PR 리뷰 워크플로우 추가 (Sequential: fetcher → analyzer → reviewer)
        - 릴리즈 노트 워크플로우 추가 (Parallel + Sequential)
        - GitHub MCP 연동 설정
        - UI: 세션 사이드바, 파일 첨부 기능 추가

        Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
*   **Commit SHA:** 5813907634ce85fd99df63d4d656a17c1dbf00ec
    *   **Author:** yhcho
    *   **Commit Message:** Initial commit: AIOK project setup

        - Python backend with FastAPI + LangChain agent
        - React + Vite frontend with chat interface
        - Google Calendar/Gmail integration tools
        - Project documentation

        Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

## v2026.03.24-e2e6 - 2026-03-24

## 🇰🇷 한국어

# Release Notes

## v2026.03.24-e2e6

## ✨ New Features

- **ADK Multi-Agent Architecture:** Transitioned to an ADK multi-agent architecture, restructuring the project layout for better organization and scalability.  The `src/aiok` directory has been moved to `app/` to follow ADK recommended practices.  Supervisor pattern implemented to enable routing after intent analysis by the `root_agent`.
- **New Workflows:**
    -  Added PR review workflow (Sequential: fetcher → analyzer → reviewer).
    -  Implemented release note workflow (Parallel + Sequential).
- **GitHub MCP Integration:** Integrated with GitHub MCP for enhanced project management capabilities.
- **UI Enhancements:** Added session sidebar and file attachment functionality to the user interface.

## 🛠️ Refactorings

- **Project Restructuring:** Refactored the project structure from `src/aiok` to `app/` to align with ADK best practices.

## 🚀 Initial Commit

- Initial commit of the AIOK project, including:
    - Python backend with FastAPI + LangChain agent.
    - React + Vite frontend with chat interface.
    - Google Calendar/Gmail integration tools.
    - Project documentation.


---

## 🇺🇸 English

# Release Notes

## v2026.03.24-e2e6

## ✨ New Features

- **ADK Multi-Agent Architecture:** Transitioned to an ADK multi-agent architecture, restructuring the project layout for better organization and scalability. The `src/aiok` directory has been moved to `app/` to follow ADK recommended practices. Supervisor pattern implemented to enable routing after intent analysis by the `root_agent`.
- **New Workflows:**
    - Added PR review workflow (Sequential: fetcher → analyzer → reviewer).
    - Implemented release note workflow (Parallel + Sequential).
- **GitHub MCP Integration:** Integrated with GitHub MCP for enhanced project management capabilities.
- **UI Enhancements:** Added session sidebar and file attachment functionality to the user interface.

## 🛠️ Refactorings

- **Project Restructuring:** Refactored the project structure from `src/aiok` to `app/` to align with ADK best practices.

## 🚀 Initial Commit

- Initial commit of the AIOK project, including:
    - Python backend with FastAPI + LangChain agent.
    - React + Vite frontend with chat interface.
    - Google Calendar/Gmail integration tools.
    - Project documentation.

## v2026.03.25 - 2026-03-25

## 🇰🇷 한국어

# Release Notes

## ✨ New Features
- automate release publication workflow (yhcho)
- GitHub 저장소 동적 지정 및 로그 패널 추가 (yhcho) - PR #1

## 🔧 Improvements
- ADK 멀티에이전트 구조로 전환 (yhcho)

## 📝 Documentation
- refresh README and presentation, unify prompt format (yhcho)
- update changelog for v2026.03.24-e2e6 (yhcho)
- update changelog for v2026.03.24-e2e4 (yhcho)
- update changelog for v2026.03.24-test (yhcho)

---

## 🇺🇸 English

# Release Notes

## ✨ New Features
- automate release publication workflow (yhcho)
- GitHub repository dynamic designation and log panel addition (yhcho) - PR #1

## 🔧 Improvements
- Transition to ADK multi-agent architecture (yhcho)

## 📝 Documentation
- refresh README and presentation, unify prompt format (yhcho)
- update changelog for v2026.03.24-e2e6 (yhcho)
- update changelog for v2026.03.24-e2e4 (yhcho)
- update changelog for v2026.03.24-test (yhcho)

