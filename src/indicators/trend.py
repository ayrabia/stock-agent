"""
Trend indicators — direction and magnitude of price movement over time.
SMAs identify which way the trend is pointing; returns measure how far it has moved.
"""

import pandas as pd


def compute_sma(close: pd.Series, period: int) -> float | None:
    """
    Simple Moving Average over `period` days.
    Price above SMA → uptrend. Price below → downtrend.
    Common periods:
      20  → short-term trend
      50  → medium-term trend
      200 → long-term trend (the "line in the sand")
    Returns None if not enough data.
    """
    if len(close) < period:
        return None
    return round(float(close.rolling(period).mean().iloc[-1]), 2)


def compute_returns(close: pd.Series) -> dict:
    """
    Percentage price returns over standard lookback windows.
    Uses approximate trading-day counts:
      1w  = 5 trading days
      1m  = 21 trading days
      3m  = 63 trading days
    Returns None for a window if insufficient history exists.
    """
    price = close.iloc[-1]

    def ret(n: int) -> float | None:
        if len(close) < n:
            return None
        return round((price / close.iloc[-n] - 1) * 100, 2)

    return {"1w": ret(5), "1m": ret(21), "3m": ret(63)}
