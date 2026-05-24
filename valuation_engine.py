"""
valuation_engine.py — ZenTrader AI
Fetches and interprets key valuation metrics + analyst consensus.
No API key needed — uses yfinance only.
"""

import yfinance as yf


# ── Sector average PE ratios (approximate 2024-25 benchmarks) ─────────────────
SECTOR_PE_BENCHMARKS = {
    "Technology": 28,
    "Financial Services": 15,
    "Healthcare": 22,
    "Consumer Cyclical": 20,
    "Consumer Defensive": 18,
    "Energy": 12,
    "Industrials": 18,
    "Basic Materials": 14,
    "Real Estate": 25,
    "Utilities": 16,
    "Communication Services": 20,
    "Unknown": 18,  # market average fallback
}


def get_valuation_metrics(ticker: str) -> dict:
    """
    Fetch all valuation metrics for a ticker.
    Returns a dict with metrics, interpretations, and analyst data.
    """
    try:
        tk = yf.Ticker(ticker)
        info = tk.info
    except Exception:
        return {"error": "Could not fetch data for this ticker."}

    sector = info.get("sector", "Unknown")
    sector_pe = SECTOR_PE_BENCHMARKS.get(sector, 18)

    # ── Raw metrics ───────────────────────────────────────────────────────────
    pe = info.get("trailingPE")
    forward_pe = info.get("forwardPE")
    pb = info.get("priceToBook")
    ps = info.get("priceToSalesTrailingTwelveMonths")
    ev_ebitda = info.get("enterpriseToEbitda")
    peg = info.get("pegRatio")
    roe = info.get("returnOnEquity")
    profit_margin = info.get("profitMargins")
    debt_equity = info.get("debtToEquity")
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    target_price = info.get("targetMeanPrice")
    target_high = info.get("targetHighPrice")
    target_low = info.get("targetLowPrice")
    recommendation = info.get("recommendationKey", "none").upper()
    num_analysts = info.get("numberOfAnalystOpinions", 0)
    earnings_growth = info.get("earningsGrowth")
    revenue_growth = info.get("revenueGrowth")
    company_name = info.get("longName", ticker)
    currency = info.get("currency", "$")

    # ── Upside / downside ─────────────────────────────────────────────────────
    upside = None
    if current_price and target_price:
        upside = round(((target_price - current_price) / current_price) * 100, 1)

    # ── Interpretation helpers ────────────────────────────────────────────────
    def interpret_pe(val):
        if val is None:
            return "N/A", "gray"
        if val < 0:
            return "Negative earnings (loss-making)", "red"
        if val < sector_pe * 0.75:
            return f"Undervalued vs sector avg ({sector_pe}x)", "green"
        if val > sector_pe * 1.5:
            return f"Expensive vs sector avg ({sector_pe}x)", "red"
        return f"Fair value vs sector avg ({sector_pe}x)", "orange"

    def interpret_pb(val):
        if val is None:
            return "N/A", "gray"
        if val < 1:
            return "Trading below book value — potential bargain", "green"
        if val < 3:
            return "Reasonable book value", "orange"
        return "High premium to book value", "red"

    def interpret_peg(val):
        if val is None:
            return "N/A", "gray"
        if val < 1:
            return "Undervalued relative to growth", "green"
        if val < 2:
            return "Fairly valued relative to growth", "orange"
        return "Overvalued relative to growth", "red"

    def interpret_ev_ebitda(val):
        if val is None:
            return "N/A", "gray"
        if val < 10:
            return "Cheap on EV/EBITDA basis", "green"
        if val < 20:
            return "Moderate EV/EBITDA", "orange"
        return "Expensive on EV/EBITDA basis", "red"

    def interpret_recommendation(rec):
        mapping = {
            "STRONG_BUY": ("Strong Buy", "green"),
            "BUY": ("Buy", "green"),
            "HOLD": ("Hold", "orange"),
            "UNDERPERFORM": ("Underperform", "red"),
            "SELL": ("Sell", "red"),
            "NONE": ("No Coverage", "gray"),
        }
        return mapping.get(rec, ("Unknown", "gray"))

    def fmt_pct(val):
        if val is None:
            return "N/A"
        return f"{val * 100:.1f}%"

    def fmt_x(val):
        if val is None:
            return "N/A"
        return f"{val:.1f}x"

    def fmt_price(val):
        if val is None:
            return "N/A"
        return f"{currency}{val:,.2f}"

    pe_interp, pe_color = interpret_pe(pe)
    pb_interp, pb_color = interpret_pb(pb)
    peg_interp, peg_color = interpret_peg(peg)
    ev_interp, ev_color = interpret_ev_ebitda(ev_ebitda)
    rec_label, rec_color = interpret_recommendation(recommendation)

    # ── Overall verdict ───────────────────────────────────────────────────────
    green_count = sum(1 for c in [pe_color, pb_color, peg_color, ev_color] if c == "green")
    red_count = sum(1 for c in [pe_color, pb_color, peg_color, ev_color] if c == "red")

    if green_count >= 3:
        verdict = "Looks Undervalued"
        verdict_color = "green"
    elif red_count >= 3:
        verdict = "Looks Overvalued"
        verdict_color = "red"
    else:
        verdict = "Fairly Valued / Mixed Signals"
        verdict_color = "orange"

    return {
        "company_name": company_name,
        "sector": sector,
        "currency": currency,
        "current_price": fmt_price(current_price),
        "verdict": verdict,
        "verdict_color": verdict_color,

        # Valuation metrics
        "metrics": [
            {
                "name": "Trailing P/E",
                "value": fmt_x(pe),
                "interpretation": pe_interp,
                "color": pe_color,
                "help": "Price divided by last 12 months earnings. Lower = cheaper.",
            },
            {
                "name": "Forward P/E",
                "value": fmt_x(forward_pe),
                "interpretation": "Based on next year earnings estimate",
                "color": "gray",
                "help": "Price divided by next 12 months estimated earnings.",
            },
            {
                "name": "Price/Book (P/B)",
                "value": fmt_x(pb),
                "interpretation": pb_interp,
                "color": pb_color,
                "help": "Price vs net asset value. Below 1 = trading below assets.",
            },
            {
                "name": "Price/Sales (P/S)",
                "value": fmt_x(ps),
                "interpretation": "Lower is generally cheaper",
                "color": "gray",
                "help": "Market cap divided by annual revenue.",
            },
            {
                "name": "EV/EBITDA",
                "value": fmt_x(ev_ebitda),
                "interpretation": ev_interp,
                "color": ev_color,
                "help": "Enterprise value vs earnings before interest/tax/depreciation. Best for comparing companies across sectors.",
            },
            {
                "name": "PEG Ratio",
                "value": fmt_x(peg),
                "interpretation": peg_interp,
                "color": peg_color,
                "help": "P/E divided by growth rate. Below 1 = undervalued relative to growth.",
            },
        ],

        # Financial health
        "health": [
            {"name": "Return on Equity", "value": fmt_pct(roe)},
            {"name": "Profit Margin", "value": fmt_pct(profit_margin)},
            {"name": "Debt/Equity", "value": fmt_x(debt_equity)},
            {"name": "Earnings Growth (YoY)", "value": fmt_pct(earnings_growth)},
            {"name": "Revenue Growth (YoY)", "value": fmt_pct(revenue_growth)},
        ],

        # Analyst consensus
        "analyst": {
            "recommendation": rec_label,
            "rec_color": rec_color,
            "num_analysts": num_analysts,
            "target_price": fmt_price(target_price),
            "target_high": fmt_price(target_high),
            "target_low": fmt_price(target_low),
            "upside": f"{upside:+.1f}%" if upside is not None else "N/A",
            "upside_color": "green" if (upside or 0) > 0 else "red",
        },
    }
