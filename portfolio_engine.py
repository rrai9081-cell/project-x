import json
import os
import streamlit as st

PORTFOLIO_FILE = "portfolio.json"

def load_portfolio():
    """Load portfolio data from local JSON file."""
    if not os.path.exists(PORTFOLIO_FILE):
        return []
    try:
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_portfolio(portfolio_data):
    """Save portfolio data to local JSON file."""
    try:
        with open(PORTFOLIO_FILE, "w") as f:
            json.dump(portfolio_data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving portfolio: {e}")
        return False

def add_to_portfolio(ticker, quantity, avg_price):
    """Add a new asset to the JSON file."""
    portfolio = load_portfolio()
    
    # Check if exists, update or append
    exists = False
    for item in portfolio:
        if item['ticker'].upper() == ticker.upper():
            # Update average price and quantity
            total_cost = (item['qty'] * item['avg_price']) + (quantity * avg_price)
            item['qty'] += quantity
            item['avg_price'] = round(total_cost / item['qty'], 2)
            exists = True
            break
            
    if not exists:
        portfolio.append({
            "ticker": ticker.upper(),
            "qty": quantity,
            "avg_price": avg_price
        })
        
    return save_portfolio(portfolio)

def suggest_ticker(name):
    """Map common Indian company names to NSE tickers."""
    mapping = {
        "RELIANCE INDUSTRIES": "RELIANCE.NS",
        "TATA CONSULTANCY": "TCS.NS",
        "HDFC BANK": "HDFCBANK.NS",
        "INFOSYS": "INFY.NS",
        "ICICI BANK": "ICICIBANK.NS",
        "HINDUSTAN UNILEVER": "HINDUNILVR.NS",
        "STATE BANK OF INDIA": "SBIN.NS",
        "BHARTI AIRTEL": "BHARTIARTL.NS",
        "ITC": "ITC.NS",
        "LARSEN & TOUBRO": "LT.NS",
        "ASIAN PAINTS": "ASIANPAINT.NS",
        "KOTAK MAHINDRA BANK": "KOTAKBANK.NS",
        "AXIS BANK": "AXISBANK.NS"
    }
    name_upper = name.upper()
    for key, ticker in mapping.items():
        if key in name_upper:
            return ticker
    # Default fallback: try joining parts and adding .NS
    clean_name = "".join(filter(str.isalnum, name.split()[0])).upper()
    return f"{clean_name}.NS"

def parse_groww_csv(df):
    """
    Parse a Groww Holdings CSV dataframe.
    Expected columns: 'Instrument', 'Qty', 'Avg Price'
    """
    imported = []
    # Normalize columns
    df.columns = [c.strip() for c in df.columns]
    
    # Map possible column names
    col_map = {
        'Instrument': ['Instrument', 'Entity', 'Stock', 'Company'],
        'Qty': ['Qty', 'Quantity', 'Holdings'],
        'Avg Price': ['Avg Price', 'Average Price', 'Buy Price']
    }
    
    found_cols = {}
    for target, options in col_map.items():
        for opt in options:
            if opt in df.columns:
                found_cols[target] = opt
                break
                
    if len(found_cols) < 3:
        return None, "Required columns not found in CSV."

    for _, row in df.iterrows():
        name = str(row[found_cols['Instrument']])
        qty = float(row[found_cols['Qty']])
        avg_p = float(row[found_cols['Avg Price']])
        
        ticker = suggest_ticker(name)
        imported.append({"ticker": ticker, "name": name, "qty": qty, "avg_price": avg_p})
        
    return imported, None

def remove_from_portfolio(ticker):
    """Remove an asset from the JSON file."""
    portfolio = load_portfolio()
    new_portfolio = [item for item in portfolio if item['ticker'].upper() != ticker.upper()]
    return save_portfolio(new_portfolio)
