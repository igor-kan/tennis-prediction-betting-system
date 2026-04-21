<!-- REPO_DOCS_REFRESH_START -->
# PLANNING

Updated: 2026-04-21
Repository: `tennis-prediction-betting-system`

## Goal
Maintain a clear execution roadmap for **tennis-prediction-betting-system** based on current codebase signals.

## Current Baseline
- Stack: Python
- Codebase scan size: 47 files (capped)
- Test signal: Test-named files detected
- CI workflows present: Yes

## Milestones
1. Stabilize
- Validate setup/run/test workflows and fix breakage.
- Document core developer workflows in README.

2. Improve
- Expand test coverage for high-change areas.
- Reduce ambiguity in command and environment setup.

3. Harden
- Strengthen reliability, release checks, and rollback notes.
- Improve operational visibility and failure handling.

4. Iterate
- Ship prioritized improvements in small, verifiable increments.
- Reassess roadmap after each release milestone.

## Exit Criteria
- Reproducible local setup and run workflow.
- Verified quality checks for critical paths.
- Docs accurately reflect real behavior and constraints.
<!-- REPO_DOCS_REFRESH_END -->

<!-- ZERO_BUDGET_PLAN:START -->
## Hosting Plan (Zero Budget)
1. Keep static-first release path in `docs/`.
2. Use GitHub Pages for public deployment.
3. Treat backend services as optional local-only tooling unless a free host exists.
4. Reject changes that introduce mandatory paid dependencies.
<!-- ZERO_BUDGET_PLAN:END -->

<!-- API_CLI_TUI_PLAN:START -->
## Interface Roadmap
1. Keep REST API as source-of-truth interface.
2. Keep CLI/TUI aligned with API endpoint changes.
3. Add smoke checks that exercise API + CLI/TUI after releases.
<!-- API_CLI_TUI_PLAN:END -->
