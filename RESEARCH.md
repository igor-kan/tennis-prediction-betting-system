<!-- REPO_DOCS_REFRESH_START -->
# RESEARCH

Updated: 2026-04-21
Repository: `tennis-prediction-betting-system`

## Focus Areas
- Domain keywords: tennis prediction betting system
- Technology stack: Python

## Open Questions
- Which modules in `tennis-prediction-betting-system` represent the highest reliability risk?
- Which external services/APIs/framework versions require compatibility validation?
- Which performance/security constraints should be tested before next release?

## Investigation Backlog
- [ ] Capture architecture notes from key paths: `backend`, `api`, `docs`, `scripts`, `.github/workflows`, `README.md`, `requirements.txt`
- [ ] Identify missing monitoring/test coverage for production-critical paths.
- [ ] Document known limitations and mitigation strategies.

## Codebase Signals
- Files scanned (capped): 47
- Common extensions: .py, .md, .sh, [no_ext], .txt, .json, .html
- Test signal: Test-named files detected
- CI workflows present: Yes

## Evidence Log
- Keep references to benchmark runs, incident notes, dependency advisories, and design decisions here.
<!-- REPO_DOCS_REFRESH_END -->

<!-- ZERO_BUDGET_RESEARCH:START -->
## Zero-Cost Hosting Research
- GitHub Pages selected as primary host for static GUI because it is free for public repositories.
- Vercel Hobby project caps can block additional deployments.
- Static-first architecture avoids recurring server and database costs.
<!-- ZERO_BUDGET_RESEARCH:END -->

<!-- API_CLI_TUI_RESEARCH:START -->
## API/CLI/TUI Notes
- API endpoints are FastAPI-native and OpenAPI-documented (`/docs`).
- CLI and TUI are lightweight clients that avoid extra dependencies.
- Shared endpoint usage reduces interface divergence risk.
<!-- API_CLI_TUI_RESEARCH:END -->
