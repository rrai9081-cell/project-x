import yfinance as yf
import pandas as pd

macros = {
    "Gold (Spot)": "GC=F",
    "Crude Oil": "CL=F",
    "USD / INR": "INR=X"
}

for name, ticker in macros.items():
    print(f"--- {name} ({ticker}) ---")
    t = yf.Ticker(ticker)
    hist = t.history(period="5d")
    print(f"Rows returned: {len(hist)}")
    if not hist.empty:
        print(hist.tail(2))
    else:
        print("No data returned")
    print("\n")
