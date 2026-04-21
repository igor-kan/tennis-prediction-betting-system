# Advanced Modeling Stack

This repository now includes a multi-model prediction stack and data pipeline scripts.

## Algorithms
- Weighted linear model on engineered features.
- Nonlinear interaction model (feature interactions + saturation).
- Momentum model emphasizing recent form/rating context.
- Optional market-implied component blend.
- Ensemble consensus with confidence based on agreement/coverage.
- Optional Platt-style calibration from labeled historical data.
- Monte Carlo simulation for probability and EV uncertainty.

## Data Pipeline Scripts
- `scripts/fetch_public_data.py`: fetches latest public scoreboard JSON.
- `scripts/build_feature_dataset.py`: converts raw JSON into training/eval CSV.
- `scripts/train_calibration.py`: trains calibration parameters from labeled rows.
- `scripts/run_advanced_backtest.py`: computes brier/logloss/ROI/drawdown metrics.
- `scripts/run_advanced_pipeline.sh`: runs the full pipeline end-to-end.

## Key Outputs
- `data/raw/*.json`
- `data/processed/feature_dataset.csv`
- `data/models/calibration.json`
- `data/reports/advanced_backtest_*.json`
