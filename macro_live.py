"""
macro_live.py — ZenTrader AI
Live INR/GBP exchange rate + Brent Crude price.
Add get_live_macro_extras() to your existing get_macro_data() in stock_engine.py
"""

import yfinance as yf


def _safe_fetch(ticker: str) -> dict:
    """Fetch price and % change safely. Returns zeros on failure."""
    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        price = (
            info.get("regularMarketPrice")
            or info.get("currentPrice")
            or tk.fast_info.get("lastPrice")
            or 0
        )
        prev = (
            info.get("regularMarketPreviousClose")
            or info.get("previousClose")
            or price
        )
        change = ((price - prev) / prev * 100) if prev else 0
        return {"price": round(float(price), 4), "change": round(float(change), 2)}
    except Exception:
        return {"price": 0, "change": 0}


def get_live_macro_extras() -> dict:
    """
    Returns live data for:
    - INR to GBP (how much £ you get per ₹)
    - GBP to INR (how much ₹ per £ — more intuitive for Indian users)
    - Brent Crude Oil (USD per barrel)

    Usage in stock_engine.py:
        from macro_live import get_live_macro_extras
        # inside get_macro_data(), merge the results:
        extras = get_live_macro_extras()
        macros.update(extras)
        return macros
    """

    # GBP/INR — how many rupees per 1 pound
    gbp_inr = _safe_fetch("GBPINR=X")

    # INR/GBP — how many pounds per 1 rupee (useful for showing conversion)
    inr_gbp = _safe_fetch("INRGBP=X")

    # Brent Crude — international oil benchmark (more relevant than WTI for India/UK)
    brent = _safe_fetch("BZ=F")

    return {
        "GBP / INR": gbp_inr,       # e.g. £1 = ₹106
        "INR / GBP": inr_gbp,       # e.g. ₹1 = £0.0094
        "Brent Crude": brent,        # e.g. $83.40 per barrel
    }


def format_gbp_inr_display(gbp_inr_price: float) -> str:
    """
    Helper: given GBP/INR rate, show how much £ you get for ₹1 lakh.
    Useful for students moving to UK — makes it personal and practical.
    """
    if gbp_inr_price <= 0:
        return "N/A"
    inr_amount = 100_000  # 1 lakh
    gbp_equivalent = inr_amount / gbp_inr_price
    return f"₹1,00,000 = £{gbp_equivalent:,.0f}"
