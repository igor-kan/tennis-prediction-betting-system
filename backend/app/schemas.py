from __future__ import annotations

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field

ProviderName = Literal["paper", "sportsbook"]
BetOutcome = Literal["won", "lost", "push"]


class EventIngestRequest(BaseModel):
    event_id: str = Field(min_length=1)
    participants: List[str] = Field(min_length=2)
    start_time_iso: str
    market_odds_decimal: float = Field(gt=1.0)
    features: Dict[str, float]


class PredictRequest(BaseModel):
    event_id: str


class PredictResponse(BaseModel):
    event_id: str
    predicted_win_probability: float
    implied_market_probability: float
    edge: float
    fair_odds_decimal: float
    confidence: float
    notes: Optional[str] = None


class StakeRecommendRequest(BaseModel):
    event_id: str
    odds_decimal_override: Optional[float] = Field(default=None, gt=1.0)


class StakeRecommendResponse(BaseModel):
    event_id: str
    recommended_stake: float
    max_allowed_stake: float
    edge: float
    confidence: float
    reason: str


class BetPlaceRequest(BaseModel):
    event_id: str
    selection: str
    odds_decimal: float = Field(gt=1.0)
    stake_amount: float = Field(gt=0)
    provider: ProviderName = "paper"


class BetPlaceResponse(BaseModel):
    accepted: bool
    ticket_id: str
    provider: ProviderName
    event_id: str
    selection: str
    stake_amount: float
    odds_decimal: float
    message: str


class BetSettleRequest(BaseModel):
    ticket_id: str
    outcome: BetOutcome


class BetSettleResponse(BaseModel):
    settled: bool
    ticket_id: str
    outcome: BetOutcome
    payout: float
    new_balance: float


class BacktestItem(BaseModel):
    event_id: str
    predicted_win_probability: float = Field(ge=0.0, le=1.0)
    odds_decimal: float = Field(gt=1.0)
    won: bool
    stake_amount: float = Field(gt=0)


class BacktestRequest(BaseModel):
    items: List[BacktestItem]


class BacktestResponse(BaseModel):
    total_staked: float
    total_return: float
    roi: float
    win_rate: float
