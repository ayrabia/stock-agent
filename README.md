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
# Run an analysis (example: AAPL)
# Open Claude Code in this directory and prompt:
# "Analyze AAPL using the stock-market-analyzer swarm and save the report to the reports folder"
```

Reports are saved to `reports/<TICKER>-<DATE>.md`.

> **Note:** The `chart-analyst` and `news-sentiment` agents require `WebSearch` permission to be enabled in Claude Code settings to retrieve live market data. Without it, technical analysis will be unavailable and sentiment/fundamentals will fall back to training knowledge.

---

## Project Structure

```
stock-agent/
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

- Agent data is bounded by Claude's knowledge cutoff unless WebSearch is enabled
- Technical analysis requires live market data access; without it, chart signals are unavailable
- Reports are informational only and not financial advice
