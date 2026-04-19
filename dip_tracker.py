from stock_engine import get_company_info

def find_bargains(tickers, threshold_pct=5.0):
    """
    Scan a list of tickers to find stocks near their 52-week low.
    threshold_pct: % distance from the low to trigger an alert.
    """
    bargains = []
    
    for symbol in tickers:
        try:
            info = get_company_info(symbol)
            curr = info.get('currentPrice', 0)
            low = info.get('fiftyTwoWeekLow', 0)
            high = info.get('fiftyTwoWeekHigh', 0)
            
            if low > 0 and curr > 0:
                # Calculate how far we are from the bottom
                dist_from_low_pct = ((curr - low) / low) * 100
                # Calculate discount from the top
                discount_from_high_pct = ((high - curr) / high) * 100 if high > 0 else 0
                
                if dist_from_low_pct <= threshold_pct:
                    bargains.append({
                        "ticker": symbol,
                        "name": info.get('shortName', symbol),
                        "current": curr,
                        "low": low,
                        "dist_low": dist_from_low_pct,
                        "discount": discount_from_high_pct
                    })
        except:
            continue
            
    # Sort by closest to bottom
    return sorted(bargains, key=lambda x: x['dist_low'])
