from textblob import TextBlob
import pandas as pd
import numpy as np

def analyze_sentiment(news_list):
    """Analyze sentiment of news headlines."""
    if not news_list:
        return 0, "Neutral"
    
    polarities = []
    for item in news_list:
        title = item.get('title', '')
        analysis = TextBlob(title)
        polarities.append(analysis.sentiment.polarity)
    
    avg_polarity = sum(polarities) / len(polarities)
    
    if avg_polarity > 0.1:
        return avg_polarity, "Positive"
    elif avg_polarity < -0.1:
        return avg_polarity, "Negative"
    else:
        return avg_polarity, "Neutral"

def calculate_intelligence_score(ticker_info, hist_df):
    """
    Calculate a beginner-friendly intelligence score based on:
    - Volatility (Standard Deviation)
    - Value (P/E Ratio comparison)
    - Momentum (Recent vs Long term avg)
    """
    try:
        # 1. Volatility Score (Lower is better for beginners)
        returns = hist_df['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) # Annualized
        vol_score = max(0, 100 - (volatility * 100))
        
        # 2. Value Score (P/E comparison)
        pe = ticker_info.get('trailingPE', 25) # Default to 25 if not found
        if pe < 15: val_score = 90
        elif pe < 25: val_score = 70
        elif pe < 40: val_score = 40
        else: val_score = 20
        
        # 3. Momentum Score
        short_ma = hist_df['Close'].tail(20).mean()
        long_ma = hist_df['Close'].tail(100).mean()
        mom_score = 80 if short_ma > long_ma else 30
        
        overall_score = (vol_score * 0.4) + (val_score * 0.3) + (mom_score * 0.3)
        
        return {
            "overall": round(overall_score),
            "volatility": "Low" if volatility < 0.2 else "Medium" if volatility < 0.4 else "High",
            "recommendation": "Strong Buy" if overall_score > 75 else "Stable" if overall_score > 50 else "Risky",
            "beginner_friendly": "Yes" if volatility < 0.25 else "No (High Volatility)"
        }
    except:
        return {"overall": 50, "volatility": "Unknown", "recommendation": "Neutral", "beginner_friendly": "Unknown"}

def get_technical_insights(df):
    """Basic technical indicators interpreted for beginners."""
    last_close = df['Close'].iloc[-1]
    ma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
    ma_50 = df['Close'].rolling(window=50).mean().iloc[-1]
    
    if last_close > ma_20 > ma_50:
        return "🔥 Strong Uptrend: Price is consistently rising."
    elif last_close < ma_20 < ma_50:
        return "❄️ Downtrend: Price is currently falling."
    else:
        return "⚖️ Consolidation: Price is moving sideways."

def analyze_macro_correlations(macro_data):
    """Interpret relationships between Global Macro and Indian Markets."""
    insights = []
    
    # 1. Crude Oil Impact
    crude = macro_data.get("Crude Oil", {})
    if crude.get("change", 0) > 1.5:
        insights.append("⛽ **Crude Alert**: Rising prices may increase inflation in India and pressure Oil Marketing companies.")
    elif crude.get("change", 0) < -1.5:
        insights.append("✅ **Crude Relief**: Lower fuel prices are generally positive for the Indian rupee and logistics sectors.")

    # 2. Gold Sentiment
    gold = macro_data.get("Gold (Spot)", {})
    if gold.get("change", 0) > 1.0:
        insights.append("🏆 **Safe Haven**: Investors are moving to Gold, which often signals uncertainty in the stock market.")

    # 3. Currency (USD/INR)
    usdinr = macro_data.get("USD / INR", {})
    if usdinr.get("change", 0) > 0.5:
        insights.append("💵 **Stronger Dollar**: Potential boost for IT and Pharma exporters, but makes imports more expensive.")
    
    return insights if insights else ["🌍 Global macro factors are currently stable."]

def interpret_market_impact(headline, ticker, portfolio_sectors):
    """Interpret news impact on specific stocks/sectors."""
    h = headline.lower()
    
    # 1. Crude Oil Impact Special Logic
    if ticker == "CL=F":
        if any(x in h for x in ['rise', 'up', 'jump', 'surge', 'spike', 'high']):
            if 'Energy' in portfolio_sectors:
                return "🟢 Bullish for your Energy stocks (Higher revenue potential).", "green"
            if any(s in portfolio_sectors for s in ['Consumer Cyclical', 'Paint', 'Airlines']):
                return "🔴 Bearish for your Transport/Paint stocks (Input costs rising).", "red"
            return "🟡 General Inflation Risk: Higher fuel costs ahead.", "gray"
        return "🔵 Stabilizing: Crude movements seem neutral for now.", "gray"
        
    # 2. General Sentiment Logic
    positive_words = ['record', 'profit', 'beat', 'growth', 'buy', 'upgrade', 'deal', 'partnership']
    negative_words = ['fall', 'drop', 'slump', 'loss', 'miss', 'downgrade', 'fraud', 'investigation']
    
    if any(w in h for w in positive_words):
        return f"🟢 Positive for {ticker}: Growth catalyst detected.", "green"
    if any(w in h for w in negative_words):
        return f"🔴 Negative for {ticker}: Risk levels increasing.", "red"
        
    return f"⚪ Update for {ticker}: Market is monitoring this development.", "gray"
