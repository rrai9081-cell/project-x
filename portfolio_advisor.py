from stock_engine import get_technical_indicators

def get_investment_advice(holding):
    """
    Generate advice for a specific holding.
    holding = {"ticker": "AAPL", "qty": 10, "avg_price": 150}
    """
    ticker = holding['ticker']
    stats = get_technical_indicators(ticker)
    
    if not stats:
        return {"signal": "Hold", "description": "Analyzing data...", "action": "Watch", "color": "gray"}
    
    rsi = stats['rsi']
    current_price = stats['current_price']
    profit_pct = ((current_price - holding['avg_price']) / holding['avg_price']) * 100
    
    # Logic for signals
    if rsi < 35:
        return {
            "signal": "Add More",
            "description": f"Stock is Oversold (RSI: {rsi}). Great time to Buy the Dip!",
            "action": "🟢 BUY",
            "color": "green"
        }
    elif rsi > 70 and profit_pct > 15:
        return {
            "signal": "Withdraw",
            "description": f"High Profit ({profit_pct:.1f}%) and Overbought. Consider taking gains.",
            "action": "🔴 SELL",
            "color": "red"
        }
    elif rsi > 65:
        return {
            "signal": "Caution",
            "description": f"Approaching expensive zone. Best to hold and wait.",
            "action": "🟡 HOLD",
            "color": "yellow"
        }
    else:
        return {
            "signal": "Stable",
            "description": "Trend is neutral. Your investment is currently balanced.",
            "action": "⚪ HOLD",
            "color": "white"
        }
