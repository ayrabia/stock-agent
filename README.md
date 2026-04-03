# Stock Market Analyzer

A multi-agent stock analysis swarm built with **RuFlo (claude-flow)**. Given a ticker symbol, it runs parallel specialist agents to produce a comprehensive investment outlook report combining technical analysis, news sentiment, and company fundamentals.

---

## How It Works

The swarm runs in two phases:

**Phase 1 — Parallel analysis** (3 agents run simultaneously):
- `chart-analyst` — technical patterns and price indicators
- `news-sentiment` — recent news and market sentiment scoring
- `fundamentals` — financial health and analyst ratings

**Phase 2 — Synthesis** (1 agent runs after Phase 1 completes):
- `synthesizer` — combines all three outputs into a final outlook report

Reports are saved to the `reports/` folder as markdown files.

---

## RuFlo (claude-flow)

This project uses **[RuFlo / claude-flow](https://github.com/ruvnet/claude-flow)** — a multi-agent swarm orchestration framework for Claude Code.

The swarm is defined in `.claude/swarm.json` and specifies:

| Setting | Value |
|---|---|
| Topology | `hierarchical` |
| Orchestrator | `claude-sonnet-4` |
| Phase 1 trigger | All 3 agents complete |
| Output format | Markdown |
| Output directory | `reports/` |

RuFlo coordinates agent lifecycle, parallel execution, context handoff between phases, and output persistence. Individual agent definitions live in `.claude/agents/` as markdown files with frontmatter declaring tools, model, and priority.

---

## Agents

### `chart-analyst`
**Role:** Technical analysis expert

Analyzes 90 days of daily price and volume data. Calculates 20-day and 50-day moving averages, RSI (overbought >70, oversold <30), and identifies chart patterns such as golden cross, death cross, and key support/resistance levels. Returns a structured summary with a bullish/bearish/neutral signal.

**Tools:** `web_search`, `computer`
**Phase:** 1

---

### `news-sentiment`
**Role:** Financial news analyst

Searches for the 5 most recent news articles about the company, recent earnings reports, analyst rating changes, and relevant macroeconomic news (tariffs, Fed policy, sector trends). Scores each item bullish/bearish/neutral and returns an overall sentiment score with the single most impactful headline.

**Tools:** `web_search`
**Phase:** 1

---

### `fundamentals`
**Role:** Fundamental analysis expert

Retrieves the current P/E ratio (vs. industry average), revenue growth across the last 4 quarters, debt-to-equity ratio, analyst consensus rating and price target, and upcoming earnings dates or corporate events. Returns a structured summary with a bullish/bearish/neutral signal in plain English.

**Tools:** `web_search`
**Phase:** 1

---

### `synthesizer`
**Role:** Senior investment analyst

Receives the full outputs of all three Phase 1 agents. Weighs technical, sentiment, and fundamental signals; identifies where agents agree or conflict; resolves disagreements with reasoned explanation; and produces a final outlook — BULLISH / BEARISH / NEUTRAL with a confidence percentage, top 2 risks, top 2 supporting reasons, and a 3-sentence plain English summary.

**Tools:** none (reasoning only)
**Phase:** 2

---

## Usage

```bash
# Quant analysis — runs all indicators from real OHLCV data (recommended)
python src/analyze.py AAPL
python src/analyze.py AAPL SNPS QCOM NVDA   # multiple tickers

# Swarm analysis — web-search-based narrative report via Claude Code prompt:
# "Analyze AAPL using the stock-market-analyzer swarm and save the report to the reports folder"
```

Reports are saved to `reports/<TICKER>-<DATE>.md`.

---

## Quant Analyzer (`src/analyze.py`)

A Python script that fetches real OHLCV data via **yfinance** (no API key required) and computes all technical indicators from scratch. Produces a markdown report and prints a terminal summary.

### Indicators Computed from Raw Data

#### RSI — Relative Strength Index (14-day)
Measures momentum — how fast and how much the price has moved recently.

```
delta      = daily price changes
avg_gain   = 14-day EWM of positive deltas
avg_loss   = 14-day EWM of negative deltas
RS         = avg_gain / avg_loss
RSI        = 100 - (100 / (1 + RS))
```

| RSI Range | Signal |
|-----------|--------|
| < 30 | Oversold — sellers exhausted, potential bounce |
| > 70 | Overbought — buyers exhausted, potential pullback |
| 30–70 | Neutral |

---

#### MACD — Moving Average Convergence Divergence (12 / 26 / 9)
Measures trend direction and momentum shifts.

```
EMA-12      = 12-day exponential moving avg of close
EMA-26      = 26-day exponential moving avg of close
MACD line   = EMA-12 − EMA-26
Signal line = 9-day EMA of MACD line
Histogram   = MACD line − Signal line
```

- MACD line **crosses above** signal → bullish momentum
- MACD line **crosses below** signal → bearish momentum
- Histogram magnitude shows acceleration

---

#### Bollinger Bands (20-day, 2σ)
Measures volatility and whether price is stretched relative to recent history.

```
Middle Band = 20-day SMA
Upper Band  = SMA + (2 × 20-day std deviation)
Lower Band  = SMA − (2 × 20-day std deviation)
%B          = (price − lower) / (upper − lower) × 100
```

| %B | Signal |
|----|--------|
| < 20% | Price near lower band — oversold |
| > 80% | Price near upper band — overbought |
| 20–80% | Normal range |

Bands widen during high volatility, narrow during consolidation.

---

#### SMA — Simple Moving Averages (20 / 50 / 200)
Measures trend direction over different timeframes.

```
SMA(n) = sum of last n closing prices / n
```

| SMA | Timeframe |
|-----|-----------|
| SMA-20 | Short-term trend |
| SMA-50 | Medium-term trend |
| SMA-200 | Long-term trend ("line in the sand") |

Price **above** SMA = bullish. Price **below** = bearish.

---

#### Golden Cross / Death Cross
Major long-term trend regime signals.

```
Golden Cross = SMA-50 crosses ABOVE SMA-200 → long-term bullish
Death Cross  = SMA-50 crosses BELOW SMA-200 → long-term bearish
```

---

#### ATR — Average True Range (14-day)
Measures daily volatility in dollar terms — useful for sizing stop-losses.

```
True Range = max(High − Low, |High − Prev Close|, |Low − Prev Close|)
ATR        = 14-day EWM average of True Range
```

A stop-loss at `price − 2×ATR` gives the trade room to breathe without being too loose.

---

#### Signal Aggregation
Five signals are each scored −1 / 0 / +1 and averaged:

| Signal | Buy (+1) | Sell (−1) |
|--------|----------|-----------|
| RSI | < 30 | > 70 |
| MACD crossover | Line above signal | Line below signal |
| Price vs SMA-50 | Above | Below |
| Price vs SMA-200 | Above | Below |
| MA Crossover | Golden Cross | Death Cross |

Average ≥ 0.5 → **BULLISH** | ≤ −0.5 → **BEARISH** | otherwise **NEUTRAL**

The final verdict layers in analyst consensus and implied upside from the price target.

---

### Dependencies

```bash
pip install yfinance pandas numpy
```

No API key required. yfinance pulls directly from Yahoo Finance.

---

## Project Structure

```
stock-agent/
├── src/
│   └── analyze.py              # Quant analyzer — yfinance + computed indicators
├── .claude/
│   ├── swarm.json              # Swarm topology and agent configuration
│   └── agents/
│       ├── chart-analyst.md    # Technical analysis agent
│       ├── news-sentiment.md   # News sentiment agent
│       ├── fundamentals.md     # Fundamentals analysis agent
│       └── synthesizer.md      # Report synthesis agent
├── reports/                    # Generated analysis reports
├── CLAUDE.md                   # Claude Code project instructions
└── README.md                   # This file
```

---

## Limitations

- `src/analyze.py` uses Yahoo Finance data — may have short delays vs. real-time feeds
- Swarm agents rely on WebSearch for live narrative data; without it they fall back to training knowledge
- Signal aggregation is rules-based, not a backtested strategy — treat as one input among many
- Reports are informational only and not financial advice
