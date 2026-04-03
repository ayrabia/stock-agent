"""
Volatility indicators — how wide price swings are.
Bollinger Bands and ATR both measure the size of recent price movement,
not the direction.
"""

import pandas as pd


def compute_bollinger(close: pd.Series, period: int = 20, std_dev: int = 2) -> dict:
    """
    Bollinger Bands — price envelope based on standard deviation.
    Middle = SMA(period)
    Upper  = Middle + std_dev × σ
    Lower  = Middle - std_dev × σ
    %B     = where current price sits within the band (0=lower, 100=upper)
      %B < 20 → price near lower band → oversold
      %B > 80 → price near upper band → overbought
    Bands widen during high volatility, narrow during consolidation.
    """
    sma        = close.rolling(period).mean()
    std        = close.rolling(period).std()
    upper      = sma + std_dev * std
    lower      = sma - std_dev * std
    price      = close.iloc[-1]
    band_width = float(upper.iloc[-1] - lower.iloc[-1])
    pct_b      = float((price - lower.iloc[-1]) / band_width) if band_width != 0 else 0.5
    return {
        "upper":  round(float(upper.iloc[-1]),  2),
        "middle": round(float(sma.iloc[-1]),    2),
        "lower":  round(float(lower.iloc[-1]),  2),
        "pct_b":  round(pct_b * 100, 1),
    }


def compute_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
    """
    Average True Range — average daily price range in dollar terms.
    True Range = max of:
      - High - Low               (intraday range)
      - |High - Previous Close|  (gap up scenario)
      - |Low  - Previous Close|  (gap down scenario)
    ATR = EWM average of True Range over `period` days.
    Useful for sizing stop-losses: stop at price - 2×ATR gives breathing room.
    """
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low  - close.shift()).abs(),
    ], axis=1).max(axis=1)
    return round(float(tr.ewm(com=period - 1, min_periods=period).mean().iloc[-1]), 2)
