from __future__ import annotations

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EventModel(Base):
    __tablename__ = "events"

    event_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    participants_json: Mapped[str] = mapped_column(Text, nullable=False)
    start_time_iso: Mapped[str] = mapped_column(String(64), nullable=False)
    market_odds_decimal: Mapped[float] = mapped_column(Float, nullable=False)
    features_json: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="manual")
    created_at_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at_ms: Mapped[int] = mapped_column(Integer, nullable=False)


class BetModel(Base):
    __tablename__ = "bets"

    ticket_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    event_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    selection: Mapped[str] = mapped_column(String(128), nullable=False)
    stake_amount: Mapped[float] = mapped_column(Float, nullable=False)
    odds_decimal: Mapped[float] = mapped_column(Float, nullable=False)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    outcome: Mapped[str | None] = mapped_column(String(16), nullable=True)
    payout: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    placed_at_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    settled_at_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)


class BankrollModel(Base):
    __tablename__ = "bankroll"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    currency: Mapped[str] = mapped_column(String(8), nullable=False)
    starting_balance: Mapped[float] = mapped_column(Float, nullable=False)
    balance: Mapped[float] = mapped_column(Float, nullable=False)
