<!-- REPO_DOCS_REFRESH_START -->
# PLANNING

Updated: 2026-04-21
Repository: `tennis-prediction-betting-system`

## Goal
Create and maintain a reliable execution roadmap for **Tennis Prediction and Betting System**.

## Context
Production-oriented repository for Tennis outcome prediction and betting execution using publicly available data.

## Milestones
1. Stabilize
- Validate setup/run/test workflows.
- Address reliability and correctness blockers.

2. Improve
- Expand automated checks and reduce fragile code paths.
- Improve developer/operator documentation.

3. Harden
- Validate deployment and rollback procedures.
- Improve observability and failure handling.

4. Iterate
- Deliver prioritized features in small, testable increments.
- Reassess roadmap after each significant release.

## Exit Criteria
- Reproducible local workflows.
- Documented and verifiable quality checks.
- Current docs reflect current behavior.
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
