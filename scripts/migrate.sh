#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../backend"
python3 - <<'PY'
from app.db import engine
from app.migrations import apply_migrations
apply_migrations(engine)
print("migrations applied")
PY
