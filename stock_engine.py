import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_stock_data(ticker_symbol, period="1y"):
    """Fetch historical stock data."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period)
        if df.empty:
            return None
        return df
    except Exception as e:
        # Silently fail for the UI but log the issue if needed
        # st.error(f"Error fetching data for {ticker_symbol}: {e}")
        return None

@st.cache_data(ttl=3600)
def get_company_info(ticker_symbol):
    """Fetch company metadata and key metrics."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        return {
            "shortName": info.get('shortName', ticker_symbol),
            "sector": info.get('sector', 'Other'),
            "industry": info.get('industry', 'Unknown'),
            "trailingPE": info.get('trailingPE', 'N/A'),
            "marketCap": info.get('marketCap', 0),
            "currency": info.get('currency', '$'),
            "currentPrice": info.get('currentPrice', 0),
            "regularMarketChangePercent": info.get('regularMarketChangePercent', 0),
            "beta": info.get('beta', 1.0), # Sensitivity to market
            "fiftyTwoWeekLow": info.get('fiftyTwoWeekLow', 0),
            "fiftyTwoWeekHigh": info.get('fiftyTwoWeekHigh', 0)
        }
    except Exception as e:
        # Handle 404/Not Found or other API issues
        return {
            "shortName": ticker_symbol,
            "sector": "Unknown",
            "industry": "Unknown",
            "trailingPE": "N/A",
            "marketCap": 0,
            "currency": "",
            "currentPrice": 0,
            "regularMarketChangePercent": 0,
            "beta": 1.0,
            "fiftyTwoWeekLow": 0,
            "fiftyTwoWeekHigh": 0,
            "error": True
        }

def get_global_indices():
    """Fetch performance of major global indices."""
    indices = {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "Nifty 50": "^NSEI",
        "FTSE 100": "^FTSE",
        "Nikkei 225": "^N225"
    }
    data = {}
    for name, ticker in indices.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                curr_close = hist['Close'].iloc[-1]
                change = ((curr_close - prev_close) / prev_close) * 100
                data[name] = {"price": curr_close, "change": change}
        except:
            continue
    return data

@st.cache_data(ttl=3600)
def get_recent_news(ticker):
    """Fetch recent news for a specific stock with fallbacks."""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        if not news:
            # Fallback 1: Try without the .NS/.BO suffix
            clean_ticker = ticker.split('.')[0]
            news = yf.Ticker(clean_ticker).news
        
        if not news:
            # Fallback 2: Global Market / Sector news
            fallback_tickers = ["^NSEI", "CL=F", "GC=F"] # Nifty, Crude, Gold
            for f_ticker in fallback_tickers:
                news = yf.Ticker(f_ticker).news
                if news: break
                
        return news if news else []
    except Exception as e:
        return []

def get_macro_data():
    """Fetch performance of key commodities and currency exchange."""
    macros = {
        "Gold (Spot)": "GC=F",
        "Crude Oil": "CL=F",
        "USD / INR": "INR=X"
    }
    data = {}
    for name, ticker in macros.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                curr_close = hist['Close'].iloc[-1]
                change = ((curr_close - prev_close) / prev_close) * 100
                data[name] = {"price": curr_close, "change": change, "ticker": ticker}
        except:
            continue
    return data

def get_nifty_50_hotlist():
    """Curated list of heavy-weight Nifty 50 companies."""
    return [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
        "HINDUNILVR.NS", "ITC.NS", "SBI.NS", "BHARTIARTL.NS", "LT.NS",
        "KOTAKBANK.NS", "AXISBANK.NS", "ADANIENT.NS", "ASIANPAINT.NS", "TITAN.NS"
    ]

def calculate_rsi(data, window=14):
    """Calculate Relative Strength Index."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_technical_indicators(ticker_symbol):
    """Fetch data and calculate indicators for AI signals."""
    df = get_stock_data(ticker_symbol, period="6mo")
    if df is None or len(df) < 20:
        return {}
    
    close = df['Close']
    rsi = calculate_rsi(close).iloc[-1]
    ma20 = close.rolling(window=20).mean().iloc[-1]
    ma50 = close.rolling(window=50).mean().iloc[-1]
    
    return {
        "rsi": round(rsi, 2),
        "ma20": round(ma20, 2),
        "ma50": round(ma50, 2),
        "current_price": round(close.iloc[-1], 2),
        "trend": "Up" if ma20 > ma50 else "Down"
    }

def get_budget_stocks(max_price):
    """Scan key high-growth potential stocks under the user's budget."""
    candidates = ["WIPRO.NS", "ITC.NS", "TATAMOTORS.NS", "ZOMATO.NS", "NHPC.NS", "RVNL.NS", "IRFC.NS", "BHEL.NS"]
    recommended = []
    
    for ticker in candidates:
        try:
            info = get_company_info(ticker)
            price = info.get('currentPrice', 999999)
            if price <= max_price:
                recommended.append({
                    "ticker": ticker,
                    "name": info.get('shortName', ticker),
                    "price": price,
                    "change": info.get('regularMarketChangePercent', 0)
                })
        except:
            continue
    return sorted(recommended, key=lambda x: x['price'], reverse=True)

def get_impact_news(portfolio_tickers):
    """Fetch news for Crude Oil and all portfolio stocks."""
    all_news = []
    global_drivers = ["CL=F", "GC=F", "INR=X"]
    for driver in global_drivers:
        try:
            feed = yf.Ticker(driver).news[:3]
            for item in feed:
                item['driver'] = driver
                all_news.append(item)
        except:
            continue
    
    for ticker in portfolio_tickers[:5]:
        try:
            feed = yf.Ticker(ticker).news[:2]
            for item in feed:
                item['driver'] = ticker
                all_news.append(item)
        except:
            continue
            
    return all_news

def get_tata_hotlist():
    """Curated list of major Tata Group companies (Comprehensive)."""
    return [
        "TCS.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TATAPOWER.NS", 
        "TATACHEM.NS", "TATACONSUM.NS", "TITAN.NS", "VOLTAS.NS", "TRENT.NS",
        "TATACOMM.NS", "TATAINVEST.NS", "TATAMETALI.NS", "NELCO.NS"
    ]

def get_tech_hotlist():
    """All major Indian Tech & IT Giants."""
    return [
        "TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", 
        "LTIM.NS", "PERSISTENT.NS", "KPITTECH.NS", "COFORGE.NS"
    ]

def get_oil_hotlist():
    """Major Oil & Energy companies in India."""
    return [
        "RELIANCE.NS", "ONGC.NS", "BPCL.NS", "IOC.NS", "HINDPETRO.NS", 
        "GAIL.NS", "OIL.NS", "PETRONET.NS"
    ]
