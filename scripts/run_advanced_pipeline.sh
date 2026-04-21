#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/fetch_public_data.py
python3 scripts/build_feature_dataset.py
python3 scripts/train_calibration.py || true
python3 scripts/run_advanced_backtest.py || true
