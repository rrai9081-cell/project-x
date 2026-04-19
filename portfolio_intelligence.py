import pandas as pd
from stock_engine import get_company_info

def analyze_portfolio_holistically(enriched_portfolio):
    """
    Analyze the full portfolio for diversification, risk, and growth.
    enriched_portfolio list of dicts: {ticker, qty, avg_price, curr_price, value, gain, advice}
    """
    if not enriched_portfolio:
        return None
    
    total_value = sum(item['value'] for item in enriched_portfolio)
    
    # 1. Sector Diversification
    sectors = {}
    for item in enriched_portfolio:
        info = get_company_info(item['ticker'])
        sector = info.get('sector', 'Other')
        sectors[sector] = sectors.get(sector, 0) + item['value']
    
    diversification = {s: round((v / total_value) * 100, 1) for s, v in sectors.items()}
    
    # 2. Risk Profile (Weighted Beta)
    total_beta = 0
    for item in enriched_portfolio:
        info = get_company_info(item['ticker'])
        beta = info.get('beta', 1.0)
        weight = item['value'] / total_value
        total_beta += beta * weight
    
    risk_level = "Growth/Aggressive" if total_beta > 1.2 else "Balanced" if total_beta > 0.8 else "Safe/Conservative"
    
    # 3. Growth Insights (Growth Focus)
    highlights = []
    
    # Sector concentration check
    max_sector = max(sectors, key=sectors.get)
    if sectors[max_sector] / total_value > 0.5:
        highlights.append(f"⚠️ **High Concentration**: {max_sector} makes up over 50% of your holdings. Growth is tied to this single sector.")
    else:
        highlights.append(f"✅ **Well Diversified**: Your money is spread across {len(sectors)} different sectors, supporting stable growth.")
    
    # Growth Potential
    best_performer = max(enriched_portfolio, key=lambda x: x['gain'])
    highlights.append(f"🚀 **Top Performer**: `{best_performer['ticker']}` is leading your portfolio's growth.")
    
    # Strategy advice
    if total_beta < 1.0:
        highlights.append("💡 **Growth Tip**: Your portfolio is currently low-risk. For higher growth, you might consider adding high-potential tech or emerging sector stocks.")
    else:
        highlights.append("💹 **Bullish Alignment**: Your portfolio has high beta, meaning it's positioned to magnify gains during a market rally.")

    return {
        "diversification": diversification,
        "risk_score": round(total_beta, 2),
        "risk_level": risk_level,
        "highlights": highlights
    }
