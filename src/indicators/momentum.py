"""
Momentum indicators — how fast and how far price has moved.
RSI and MACD both answer: is buying/selling pressure accelerating or exhausted?
"""

import pandas as pd
import numpy as np


def compute_rsi(close: pd.Series, period: int = 14) -> float:
    """
    Relative Strength Index.
    Compares average gains vs average losses over `period` days.
      < 30 → oversold (sellers exhausted)
      > 70 → overbought (buyers exhausted)
    """
    delta    = close.diff()
    gain     = delta.clip(lower=0)
    loss     = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs  = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return round(float(rsi.iloc[-1]), 2)


def compute_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """
    Moving Average Convergence Divergence.
    MACD line  = EMA(fast) - EMA(slow)       — trend direction
    Signal line = EMA(MACD, signal)           — smoothed trigger
    Histogram   = MACD - Signal               — momentum acceleration
    Crossover: MACD above signal → BULLISH, below → BEARISH
    """
    ema_fast    = close.ewm(span=fast,   adjust=False).mean()
    ema_slow    = close.ewm(span=slow,   adjust=False).mean()
    macd_line   = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram   = macd_line - signal_line
    return {
        "macd":      round(float(macd_line.iloc[-1]),   3),
        "signal":    round(float(signal_line.iloc[-1]), 3),
        "histogram": round(float(histogram.iloc[-1]),   3),
        "crossover": "BULLISH" if macd_line.iloc[-1] > signal_line.iloc[-1] else "BEARISH",
    }
