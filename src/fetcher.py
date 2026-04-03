"""
Data fetching via yfinance.
Returns a single dict with all price, technical, and fundamental data
ready for report generation.
"""

from datetime import datetime
import yfinance as yf

from indicators import (
    compute_rsi, compute_macd, compute_bollinger,
    compute_sma, compute_returns, compute_atr, signal_summary,
)


def fetch_data(ticker_sym: str) -> dict:
    tk = yf.Ticker(ticker_sym)

    # ── Price history ─────────────────────────────────────────────────────────
    hist = tk.history(period="1y", interval="1d", auto_adjust=True)
    if hist.empty:
        raise ValueError(f"No price data found for {ticker_sym}")

    close = hist["Close"]
    high  = hist["High"]
    low   = hist["Low"]
    vol   = hist["Volume"]

    price       = round(float(close.iloc[-1]), 2)
    prev_close  = round(float(close.iloc[-2]), 2)
    daily_chg   = round(price - prev_close, 2)
    daily_chg_p = round((daily_chg / prev_close) * 100, 2)

    # ── Technical indicators ──────────────────────────────────────────────────
    rsi       = compute_rsi(close)
    macd_info = compute_macd(close)
    bb        = compute_bollinger(close)
    sma20     = compute_sma(close, 20)
    sma50     = compute_sma(close, 50)
    sma200    = compute_sma(close, 200)
    returns   = compute_returns(close)
    atr_val   = compute_atr(high, low, close)

    week_high  = round(float(close.tail(252).max()), 2)
    week_low   = round(float(close.tail(252).min()), 2)
    avg_vol_30 = int(vol.tail(30).mean())

    crossover   = "GOLDEN CROSS" if (sma50 and sma200 and sma50 > sma200) else "DEATH CROSS"
    tech_signal = signal_summary(rsi, macd_info, price, sma50, sma200)

    # ── Fundamentals ──────────────────────────────────────────────────────────
    info = tk.info or {}

    def g(key, default=None):
        v = info.get(key, default)
        return v if v not in (None, "N/A", "None", float("inf"), float("-inf")) else default

    def pct(v):
        return round(v * 100, 2) if v else None

    fundamentals = {
        "name":            g("longName", ticker_sym),
        "sector":          g("sector"),
        "industry":        g("industry"),
        "market_cap":      g("marketCap"),
        "pe_trailing":     g("trailingPE"),
        "pe_forward":      g("forwardPE"),
        "peg":             g("pegRatio"),
        "ps_ratio":        g("priceToSalesTrailing12Months"),
        "pb_ratio":        g("priceToBook"),
        "ev_ebitda":       g("enterpriseToEbitda"),
        "revenue_ttm":     g("totalRevenue"),
        "revenue_growth":  pct(g("revenueGrowth")),
        "earnings_growth": pct(g("earningsGrowth")),
        "gross_margin":    pct(g("grossMargins")),
        "op_margin":       pct(g("operatingMargins")),
        "net_margin":      pct(g("profitMargins")),
        "roe":             pct(g("returnOnEquity")),
        "roa":             pct(g("returnOnAssets")),
        "total_cash":      g("totalCash"),
        "total_debt":      g("totalDebt"),
        "free_cashflow":   g("freeCashflow"),
        "op_cashflow":     g("operatingCashflow"),
        "de_ratio":        g("debtToEquity"),
        "current_ratio":   g("currentRatio"),
        "dividend_yield":  pct(g("dividendYield")),
        "payout_ratio":    pct(g("payoutRatio")),
        "eps_ttm":         g("trailingEps"),
        "eps_forward":     g("forwardEps"),
        "analyst_target":  g("targetMeanPrice"),
        "analyst_low":     g("targetLowPrice"),
        "analyst_high":    g("targetHighPrice"),
        "recommendation":  g("recommendationKey"),
        "num_analysts":    g("numberOfAnalystOpinions"),
        "beta":            g("beta"),
        "short_ratio":     g("shortRatio"),
        "shares_out":      g("sharesOutstanding"),
        "float_shares":    g("floatShares"),
        "next_earnings":   g("earningsTimestamp"),
    }

    # ── Analyst recommendations ───────────────────────────────────────────────
    try:
        recs = tk.recommendations
        recent_recs = recs.tail(5).to_dict("records") if (recs is not None and not recs.empty) else []
    except Exception:
        recent_recs = []

    # ── News headlines ────────────────────────────────────────────────────────
    try:
        news = [
            {
                "title":     n.get("content", {}).get("title", n.get("title", "")),
                "publisher": n.get("content", {}).get("provider", {}).get("displayName", n.get("publisher", "")),
            }
            for n in (tk.news or [])[:6]
        ]
    except Exception:
        news = []

    return {
        "ticker":      ticker_sym.upper(),
        "date":        datetime.now().strftime("%Y-%m-%d"),
        "price":       price,
        "prev_close":  prev_close,
        "daily_chg":   daily_chg,
        "daily_chg_p": daily_chg_p,
        "52w_high":    week_high,
        "52w_low":     week_low,
        "avg_vol_30d": avg_vol_30,
        "atr":         atr_val,
        "returns":     returns,
        "rsi":         rsi,
        "macd":        macd_info,
        "bollinger":   bb,
        "sma20":       sma20,
        "sma50":       sma50,
        "sma200":      sma200,
        "crossover":   crossover,
        "tech_signal": tech_signal,
        "fundamentals": fundamentals,
        "recent_recs": recent_recs,
        "news":        news,
    }
