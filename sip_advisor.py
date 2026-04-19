import pandas as pd
import numpy as np

def generate_monthly_basket(budget, budget_stocks):
    """
    Suggest a 500-rupee basket from available stocks.
    Focus on High Growth (as requested).
    """
    if not budget_stocks:
        return []
    
    # Priority for High Growth tickers
    high_growth_tickers = ["ZOMATO.NS", "RVNL.NS", "IRFC.NS", "TATAMOTORS.NS"]
    
    basket = []
    rem_budget = budget
    
    # Sort stocks to try and fit high-growth first
    sorted_stocks = sorted(budget_stocks, key=lambda x: x['ticker'] in high_growth_tickers, reverse=True)
    
    for stock in sorted_stocks:
        if stock['price'] <= rem_budget:
            basket.append(stock)
            rem_budget -= stock['price']
            break # Just one primary pick for a small budget to build a strong position
            
    return basket

def calculate_compounding(monthly_investment, annual_return=0.15, years=20):
    """
    Project future value of monthly investments.
    Default 15% for High Growth strategy.
    """
    months = np.arange(1, (years * 12) + 1)
    fv = []
    r_monthly = annual_return / 12
    
    for m in months:
        # Formula: P * [((1 + r)^n - 1) / r] * (1 + r)
        value = monthly_investment * (((1 + r_monthly)**m - 1) / r_monthly) * (1 + r_monthly)
        fv.append(value)
        
    df = pd.DataFrame({
        "Month": months,
        "Year": months / 12,
        "Projected Value": fv
    })
    return df
