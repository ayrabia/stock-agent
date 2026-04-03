"""
Signal aggregation — combines individual indicator readings into a
single BULLISH / NEUTRAL / BEARISH label.

Scoring table (each signal contributes -2 to +2):
  RSI < 30       → +2   (strongly oversold)
  RSI 30–45      → +1   (mild oversold)
  RSI 55–70      → -1   (mild overbought)
  RSI > 70       → -2   (strongly overbought)
  MACD crossover → ±1
  Price vs SMA50 → ±1
  Price vs SMA200→ ±1
  Golden/Death X → ±1   (SMA50 vs SMA200)

Average ≥ +1.0 → BULLISH
Average ≤ -1.0 → BEARISH
Otherwise      → NEUTRAL
"""


def signal_summary(
    rsi: float,
    macd_info: dict,
    price: float,
    sma50: float | None,
    sma200: float | None,
) -> str:
    scores = []

    # RSI — weighted ±2 at extremes
    if rsi < 30:
        scores.append(2)
    elif rsi < 45:
        scores.append(1)
    elif rsi > 70:
        scores.append(-2)
    elif rsi > 55:
        scores.append(-1)
    else:
        scores.append(0)

    # MACD line vs signal line
    scores.append(1 if macd_info["crossover"] == "BULLISH" else -1)

    # Price position relative to moving averages
    if sma50:
        scores.append(1 if price > sma50 else -1)
    if sma200:
        scores.append(1 if price > sma200 else -1)

    # Golden cross / death cross
    if sma50 and sma200:
        scores.append(1 if sma50 > sma200 else -1)

    avg = sum(scores) / len(scores)
    if avg >= 1.0:
        return "BULLISH"
    if avg <= -1.0:
        return "BEARISH"
    return "NEUTRAL"
