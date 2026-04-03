#!/usr/bin/env python3
"""
Stock Market Analyzer — entry point.
Usage: python src/analyze.py AAPL
       python src/analyze.py AAPL SNPS QCOM
"""

import sys
import os

from fetcher import fetch_data
from report import generate_report, overall_verdict, fmt_big, rsi_label


REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")


def analyze(ticker_sym: str) -> None:
    print(f"\n{'='*60}")
    print(f"  Analyzing {ticker_sym.upper()} ...")
    print(f"{'='*60}")

    try:
        data = fetch_data(ticker_sym)
    except Exception as e:
        print(f"  ERROR: {e}")
        return

    report  = generate_report(data)
    verdict = overall_verdict(data)
    f       = data["fundamentals"]
    target  = f.get("analyst_target")
    upside  = round((target / data["price"] - 1) * 100, 1) if target and data["price"] else None

    # Save report
    os.makedirs(REPORTS_DIR, exist_ok=True)
    fname = f"{data['ticker']}_{data['date']}_quant.md"
    fpath = os.path.join(REPORTS_DIR, fname)
    with open(fpath, "w") as fp:
        fp.write(report)

    # Terminal summary
    print(f"\n  Name:        {f.get('name', ticker_sym)}")
    print(f"  Price:       ${data['price']}  ({data['daily_chg_p']:+.2f}% today)")
    print(f"  52w Range:   ${data['52w_low']} – ${data['52w_high']}")
    print(f"  RSI (14):    {rsi_label(data['rsi'])}")
    print(f"  MACD:        {data['macd']['macd']} ({data['macd']['crossover']})")
    print(f"  SMA-50:      ${data['sma50']}  |  SMA-200: ${data['sma200']}")
    print(f"  Crossover:   {data['crossover']}")
    print(f"  Tech Signal: {data['tech_signal']}")
    print(f"  Fwd P/E:     {f.get('pe_forward')}x  |  FCF: {fmt_big(f.get('free_cashflow'))}")
    if upside is not None:
        print(f"  Analyst:     {(f.get('recommendation') or 'N/A').upper()}  |  Target: ${target}  ({upside:+.1f}% upside)")
    print(f"\n  {'─'*40}")
    print(f"  VERDICT:  {verdict}")
    print(f"  {'─'*40}")
    print(f"\n  Report saved: {fpath}\n")


if __name__ == "__main__":
    tickers = sys.argv[1:] if len(sys.argv) > 1 else ["AAPL"]
    for t in tickers:
        analyze(t)
