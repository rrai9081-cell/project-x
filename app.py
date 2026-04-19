import streamlit as st
from stock_engine import get_stock_data, get_company_info, get_global_indices, get_recent_news, get_macro_data, get_nifty_50_hotlist, get_technical_indicators, get_budget_stocks, get_impact_news, get_tata_hotlist, get_oil_hotlist, get_tech_hotlist
from ai_analyzer import analyze_sentiment, calculate_intelligence_score, get_technical_insights, analyze_macro_correlations, interpret_market_impact
from ui_components import metric_card, beginner_badge, section_header, educational_box, load_local_css, macro_header, incident_card, advice_badge, privacy_mask, groww_export_guide, budget_stock_card, impact_news_card, bargain_alert_card
from portfolio_engine import load_portfolio, add_to_portfolio, remove_from_portfolio, parse_groww_csv
from portfolio_advisor import get_investment_advice
from portfolio_intelligence import analyze_portfolio_holistically
from sip_advisor import generate_monthly_basket, calculate_compounding
from dip_tracker import find_bargains
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="ZenTrader AI: Global Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
load_local_css("assets/styles.css")

# Session State for User Experience
if 'privacy_on' not in st.session_state:
    st.session_state.privacy_on = False

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ ZenTrader AI")
    st.markdown("---")
    
    # 🌍 Global Pulse (Macros)
    st.subheader("Global Pulse")
    macros = get_macro_data()
    mcol1, mcol2 = st.columns(2)
    with mcol1:
        gold = macros.get("Gold (Spot)", {"price": 0, "change": 0})
        macro_header("Gold", f"${gold['price']:,.1f}", gold['change'])
        usdinr = macros.get("USD / INR", {"price": 0, "change": 0})
        macro_header("USD/INR", f"₹{usdinr['price']:.2f}", usdinr['change'])
    with mcol2:
        crude = macros.get("Crude Oil", {"price": 0, "change": 0})
        macro_header("Crude Oil", f"${crude['price']:,.2f}", crude['change'])

    st.markdown("---")
    
    ticker_input = st.text_input("Search Global Symbols:", value="RELIANCE.NS", help="Try: AAPL, TSLA, TCS.NS, INR=X")
    # Time Horizon Slider with friendly labels
    horizon_labels = ["1 Day", "5 Days", "1 Month", "3 Months", "6 Months", "1 Year", "2 Years", "5 Years", "Max"]
    PERIOD_MAP = {
        "1 Day": "1d", "5 Days": "5d", "1 Month": "1mo", "3 Months": "3mo", 
        "6 Months": "6mo", "1 Year": "1y", "2 Years": "2y", "5 Years": "5y", "Max": "max"
    }
    
    selected_label = st.select_slider("Select Time Horizon", options=horizon_labels, value="1 Year")
    selected_period = PERIOD_MAP[selected_label]
    
    st.markdown("---")
    st.subheader("Index Performance")
    indices = get_global_indices()
    for name, data in indices.items():
        color = "green" if data['change'] > 0 else "red"
        st.markdown(f"**{name}**: {data['price']:,.2f} <span style='color:{color}'>({data['change']:+.2f}%)</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📈 Visualization Settings")
    chart_style = st.radio("Chart Type", ["Candlestick", "Area Chart (Modern)", "Bar Chart (Momentum)"], index=0)
    
    st.markdown("---")
    privacy_on = st.toggle("Privacy Mode (Hide my Money)", value=st.session_state.privacy_on)
    st.session_state.privacy_on = privacy_on
    
    if st.button("🎓 Open Beginner Hub"):
        st.session_state.show_edu = True
        st.rerun()

# --- MAIN CONTENT ---
st.title("Global Stock Intelligence AI")
st.markdown(f"**Market Date**: {datetime.now().strftime('%B %d, %Y')}")

# Tabs for different views
tab_analysis, tab_nifty, tab_portfolio = st.tabs(["📊 Stock Intelligence", "🇮🇳 Indian Markets Hotlist", "💼 My Private Portfolio"])

with tab_analysis:
    # Fetch Data
    with st.spinner(f"Analyzing {ticker_input}..."):
        hist_df = get_stock_data(ticker_input, period=selected_period)
        info = get_company_info(ticker_input)
        news = get_recent_news(ticker_input)

    if hist_df is not None and not hist_df.empty:
        # Macro Correlation Insights (Dynamic)
        macro_insights = analyze_macro_correlations(macros)
        with st.expander("🌍 Live Macro & Incident Watch", expanded=True):
            for insight in macro_insights:
                st.write(insight)

        # Top Metrics Bar
        col1, col2, col3, col4 = st.columns(4)
        
        curr_price = hist_df['Close'].iloc[-1]
        
        # Handle cases with only 1 data point (e.g. 1d horizon)
        if len(hist_df) >= 2:
            prev_price = hist_df['Close'].iloc[-2]
            price_change = ((curr_price - prev_price) / prev_price) * 100
        else:
            prev_price = curr_price
            price_change = 0.0
        
        with col1:
            symbol_currency = info.get('currency', '$')
            metric_card("Current Price", f"{symbol_currency}{curr_price:,.2f}", f"{price_change:+.2f}%", help_text="Latest trading price.")
        with col2:
            pe_ratio = info.get('trailingPE', 'N/A')
            metric_card("P/E Ratio", f"{pe_ratio}", help_text="Price-to-Earnings: Cheap vs Expensive.")
        with col3:
            mkt_cap = info.get('marketCap', 0) / 1e9
            metric_card("Market Cap", f"${mkt_cap:,.1f}B", help_text="Total company value.")
        with col4:
            sentiment_score, sentiment_label = analyze_sentiment(news)
            metric_card("Market Sentiment", sentiment_label, f"Score: {sentiment_score:.2f}", help_text="AI Analysis of news.")

        st.markdown("---")

        # Main Chart & AI Insights
        main_col, side_col = st.columns([2, 1])

        with main_col:
            section_header("Price Intelligence", "Interactive history & trend analysis")
            fig = go.Figure()
            
            if chart_style == "Candlestick":
                fig.add_trace(go.Candlestick(
                    x=hist_df.index, open=hist_df['Open'], high=hist_df['High'], low=hist_df['Low'], close=hist_df['Close'], name="Price"
                ))
            elif chart_style == "Area Chart (Modern)":
                # Premium Area Chart
                fig.add_trace(go.Scatter(
                    x=hist_df.index, y=hist_df['Close'], name="Price",
                    fill='tozeroy', line=dict(color='#007BFF', width=2),
                    fillcolor='rgba(0, 123, 255, 0.1)'
                ))
            else:
                # Momentum Bar Chart
                hist_df['color'] = ['#28A745' if c >= o else '#DC3545' for o, c in zip(hist_df['Open'], hist_df['Close'])]
                fig.add_trace(go.Bar(
                    x=hist_df.index, y=hist_df['Close'], name="Price",
                    marker_color=hist_df['color'], opacity=0.8
                ))

            # Add Moving Average
            hist_df['MA50'] = hist_df['Close'].rolling(window=50).mean()
            fig.add_trace(go.Scatter(x=hist_df.index, y=hist_df['MA50'], name="50-Day Avg", line=dict(color='#FFD700', width=1, dash='dot')))
            
            fig.update_layout(template="plotly_white", xaxis_rangeslider_visible=False, 
                              margin=dict(l=0, r=0, t=10, b=0), height=450, 
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, width='stretch')

        with side_col:
            section_header("AI Intelligence Report")
            intel = calculate_intelligence_score(info, hist_df)
            st.write(f"### Score: {intel['overall']}/100")
            st.progress(intel['overall'] / 100)
            beginner_badge(intel['beginner_friendly'])
            st.markdown(f"**Volatility**: `{intel['volatility']}`")
            st.markdown("---")
            st.info(get_technical_insights(hist_df))
            
            section_header("Recent Incidents", "Events influencing this stock")
            if not news:
                st.info("No specific news incidents found for this ticker.")
            else:
                for item in news[:5]:
                    # Determine if it's a fallback (doesn't contain ticker in title)
                    is_fallback = ticker_input.lower() not in item.get('title', '').lower()
                    tag = "Market" if is_fallback else "Direct"
                    incident_card(item.get('title', 'Market Update'), item.get('publisher', 'Finance Source'), tag, item.get('summary', 'Latest market update...'))
            
            if len(news) > 5:
                with st.expander("🔍 View All Market Incidents"):
                    for item in news[5:]:
                        st.markdown(f"**{item.get('publisher', 'News')}**: {item.get('title', 'Market Update')}")
                        st.caption(f"Time: {datetime.now().strftime('%H:%M')} | [Read More]({item.get('link', '#')})")
                        st.markdown("---")
    else:
        st.warning(f"⚠️ Could not find data for '{ticker_input}'. Please check the symbol in the sidebar.")
        st.info("Try common symbols like: AAPL (Apple), TSLA (Tesla), BTC-USD (Bitcoin), or RELIANCE.NS (Reliance India).")

with tab_nifty:
    section_header("🇮🇳 Indian Market Sectors", "Deep dives into top groups and industries")
    
    sub_tab_nifty, sub_tab_tata, sub_tab_oil, sub_tab_tech = st.tabs(["Nifty 50 Hub", "Tata Group Powerhouse", "Oil & Energy Hub", "Tech Giants Hub"])
    
    def render_sector_grid(tickers):
        n_cols = 3
        rows = [tickers[i:i + n_cols] for i in range(0, len(tickers), n_cols)]
        for row in rows:
            cols = st.columns(n_cols)
            for i, ticker in enumerate(row):
                with cols[i]:
                    n_info = get_company_info(ticker)
                    n_name = n_info.get('shortName', ticker)
                    n_price = n_info.get('currentPrice', 0)
                    n_change = n_info.get('regularMarketChangePercent', 0)
                    color = "green" if n_change > 0 else "red"
                    st.markdown(f"""
                    <div style="background: #F8F9FA; padding: 15px; border-radius: 8px; border: 1px solid rgba(0,0,0,0.08);">
                        <div style="font-size: 0.8rem; color: #6C757D;">{ticker}</div>
                        <div style="font-weight: 700; font-size: 1.1rem; color: #212529;">{n_name}</div>
                        <div style="font-size: 1rem; color: #212529;">₹{n_price:,.2f} <span style="color: {color};">({n_change:+.2f}%)</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("") # Spacer

    with sub_tab_nifty:
        render_sector_grid(get_nifty_50_hotlist())
    
    with sub_tab_tata:
        render_sector_grid(get_tata_hotlist())
        
    with sub_tab_oil:
        render_sector_grid(get_oil_hotlist())
        
    with sub_tab_tech:
        render_sector_grid(get_tech_hotlist())

with tab_portfolio:
    section_header("💼 My Private Portfolio", "Track your assets & get AI investment signals")
    
    # --- NEW: AI Bargain Finder (Buy the Dip) ---
    p_tickers = [i['ticker'] for i in load_portfolio()]
    watch_list = list(set(p_tickers + get_tata_hotlist() + get_oil_hotlist()[:3]))
    
    with st.expander("💎 AI Bargain Finder (Buy the Dip)", expanded=False):
        st.markdown("<p style='font-size: 0.85rem; color: #6C757D;'>Scanning for stocks trading within 5% of their yearly bottom...</p>", unsafe_allow_html=True)
        bargains = find_bargains(watch_list, threshold_pct=5.0)
        if not bargains:
            st.info("No major bargains detected right now. Markets are trading away from yearly lows.")
        else:
            bcol1, bcol2 = st.columns(2)
            for idx, b in enumerate(bargains[:4]):
                with (bcol1 if idx % 2 == 0 else bcol2):
                    bargain_alert_card(b['name'], b['ticker'], b['current'], b['low'], b['dist_low'], b['discount'])

    # Portfolio Actions
    p_col1, p_col2 = st.columns([1, 2])
    
    with p_col1:
        st.markdown("### ➕ Add Investment")
        add_tab, import_tab = st.tabs(["Manual Add", "Bulk Import (Groww)"])
        
        with add_tab:
            with st.form("add_asset_form"):
                new_ticker = st.text_input("Ticker Symbol", placeholder="e.g. AAPL or TCS.NS")
                new_qty = st.number_input("Quantity", min_value=0.01, step=0.01)
                new_price = st.number_input("Avg Purchase Price", min_value=0.01, step=0.01)
                if st.form_submit_button("Add to Portfolio"):
                    if new_ticker:
                        add_to_portfolio(new_ticker, new_qty, new_price)
                        st.success(f"Added {new_ticker} to your local storage!")
                        st.rerun()
                    else:
                        st.error("Please enter a ticker symbol.")

        with import_tab:
            groww_export_guide()
            uploaded_file = st.file_uploader("Upload Groww Holdings CSV", type=["csv", "xlsx"])
            if uploaded_file:
                df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                assets, error = parse_groww_csv(df)
                if error:
                    st.error(error)
                else:
                    st.markdown("### 🔍 Mapping Results")
                    for a in assets:
                        st.write(f"🏷️ {a['name']} → `{a['ticker']}`")
                    if st.button("Confirm & Import All"):
                        for a in assets:
                            add_to_portfolio(a['ticker'], a['qty'], a['avg_price'])
                        st.success(f"Successfully imported {len(assets)} holdings!")
                        st.rerun()

    with p_col2:
        portfolio = load_portfolio()
        if not portfolio:
            st.info("Your portfolio is currently empty. Add your first asset using the form on the left.")
        else:
            # Summary Metrics for Portfolio
            total_value = 0
            total_gain = 0
            
            # Fetch current prices for all
            enriched_portfolio = []
            for item in portfolio:
                stats = get_technical_indicators(item['ticker'])
                curr_p = stats.get('current_price', item['avg_price'])
                val = curr_p * item['qty']
                gain = val - (item['avg_price'] * item['qty'])
                
                total_value += val
                total_gain += gain
                
                # Get AI Advice
                advice = get_investment_advice(item)
                enriched_portfolio.append({**item, "curr_price": curr_p, "value": val, "gain": gain, "advice": advice})

            if len(portfolio) > 2:
                with st.expander("🔮 AI Portfolio Health Report (Growth Focused)", expanded=True):
                    report = analyze_portfolio_holistically(enriched_portfolio)
                    if report:
                        hcol1, hcol2 = st.columns([1, 1.5])
                        with hcol1:
                            # Sector Pie Chart
                            df_div = pd.DataFrame(list(report['diversification'].items()), columns=['Sector', 'Percentage'])
                            fig_div = px.pie(df_div, values='Percentage', names='Sector', hole=0.4,
                                            color_discrete_sequence=px.colors.sequential.Teal)
                            fig_div.update_layout(showlegend=False, height=250, margin=dict(l=0, r=0, t=0, b=0),
                                                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                            st.plotly_chart(fig_div, width='stretch')
                        
                        with hcol2:
                            st.markdown(f"**Growth Strategy**: `{report['risk_level']}`")
                            st.markdown(f"**Portfolio Beta**: `{report['risk_score']}`")
                            for highlight in report['highlights']:
                                st.write(highlight)

            # --- NEW: AI Market Impact Feed ---
            st.markdown("---")
            section_header("📡 AI Market Impact Feed", "Connecting global news to your money")
            
            # Aggregate data for impact analysis
            p_tickers = [i['ticker'] for i in portfolio]
            p_sectors = [get_company_info(t).get('sector', 'Other') for t in p_tickers]
            
            with st.spinner("Decoding latest market signals..."):
                impact_news = get_impact_news(p_tickers)
                
            if not impact_news:
                st.info("No major market-moving news detected in the last few hours.")
            else:
                ncol1, ncol2 = st.columns(2)
                for idx, item in enumerate(impact_news[:6]): # Show top 6
                    with (ncol1 if idx % 2 == 0 else ncol2):
                        interp, color = interpret_market_impact(item['title'], item['driver'], p_sectors)
                        impact_news_card(item['title'], item.get('publisher', 'News'), item['driver'], interp, color)

            # --- Smart Salary Advisor ---
            st.markdown("---")
            section_header("🎯 Smart Salary Advisor", "Make the most of your ₹500 monthly investment")
            
            acol1, acol2 = st.columns([1, 2])
            with acol1:
                monthly_amt = st.number_input("Monthly Budget (₹)", value=500, step=100)
                b_stocks = get_budget_stocks(monthly_amt)
                
                if not b_stocks:
                    st.warning(f"No high-growth stocks found under ₹{monthly_amt}. Try slightly increasing your budget.")
                else:
                    basket = generate_monthly_basket(monthly_amt, b_stocks)
                    st.markdown("### 🧺 This Month's Basket")
                    for b in basket:
                        budget_stock_card(b['name'], b['ticker'], b['price'], b['change'])
                    st.caption("Focus: High Growth Companies")
            
            with acol2:
                st.markdown("### 🚀 Compounding Your ₹500")
                comp_df = calculate_compounding(monthly_amt, years=15)
                fig_comp = px.line(comp_df, x="Year", y="Projected Value", title=f"Value over 15 Years @ 15% Returns")
                fig_comp.update_layout(template="plotly_white", height=300, 
                                     paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_comp, width='stretch')
                
                final_val = comp_df['Projected Value'].iloc[-1]
                st.success(f"By investing just ₹{monthly_amt} every month, your wealth could grow to approx **₹{final_val:,.0f}** in 15 years!")

            st.markdown("---")
            scol1, scol2 = st.columns(2)
            with scol1:
                metric_card("Total Portfolio Value", privacy_mask(total_value, privacy_on), help_text="Current liquid value of all your holdings.")
            with scol2:
                gain_pct = (total_gain / (total_value - total_gain)) * 100 if (total_value - total_gain) != 0 else 0
                metric_card("Net Lifetime P&L", privacy_mask(total_gain, privacy_on), f"{gain_pct:+.2f}%", help_text="Total unrealized profit or loss.")

            st.markdown("---")
            st.markdown("### 📋 Holding Intelligence")
            
            # Custom Table
            header_cols = st.columns([1, 1, 1, 1, 1, 2])
            header_cols[0].markdown("**Ticker**")
            header_cols[1].markdown("**Qty**")
            header_cols[2].markdown("**Avg Cost**")
            header_cols[3].markdown("**Current**")
            header_cols[4].markdown("**P&L**")
            header_cols[5].markdown("**AI Advisor Signaling**")
            
            for item in enriched_portfolio:
                row_cols = st.columns([1, 1, 1, 1, 1, 2])
                row_cols[0].markdown(f"`{item['ticker']}`")
                row_cols[1].markdown(f"{item['qty']}")
                row_cols[2].markdown(privacy_mask(item['avg_price'], privacy_on))
                row_cols[3].markdown(privacy_mask(item['curr_price'], privacy_on))
                row_cols[4].markdown(f"<span style='color: {'#00FF87' if item['gain'] >= 0 else '#FF4B4B'}'>{privacy_mask(item['gain'], privacy_on)}</span>", unsafe_allow_html=True)
                
                # Advice Tooltip/Signal
                adv = item['advice']
                row_cols[5].markdown(f"{advice_badge(adv['action'], adv['color'])} <span style='font-size: 0.8rem; color: #6C757D;'>{adv['description']}</span>", unsafe_allow_html=True)

            st.markdown("---")
            with st.expander("🛠️ Portfolio Management"):
                del_ticker = st.selectbox("Select Asset to Remove", options=[i['ticker'] for i in portfolio])
                if st.button("Delete Selected Asset"):
                    remove_from_portfolio(del_ticker)
                    st.warning(f"Removed {del_ticker} from local storage.")
                    st.rerun()

# Educational Section (Conditional)
if st.session_state.get('show_edu', False):
        st.markdown("---")
        section_header("🎓 Beginner Education Hub", "Understanding the charts & terms")
        ecol1, ecol2, ecol3 = st.columns(3)
        with ecol1:
            educational_box("What is a Candlestick?", "The 'rectangular' shapes on the chart. Green means the price went up that day, red means it went down.")
            educational_box("What is Market Cap?", "Total value. Imagine if you wanted to buy the WHOLE company, this is the price tag.")
            educational_box("Dividends", "A portion of company profits shared with you just for owning the stock. Like interest in a bank.")
        with ecol2:
            educational_box("What is P/E Ratio?", "Cheap vs. Expensive. High P/E might mean people expect high growth, low P/E might mean it's a bargain.")
            educational_box("What is Volatility?", "How much the price swings. High volatility is like a roller coaster—exciting but risky!")
            educational_box("Volume", "The total number of shares traded today. High volume means lots of people are interested.")
        with ecol3:
            educational_box("RSI (Strength)", "Relative Strength Index. If it's over 70, the stock might be too expensive. Under 30, it might be a bargain.")
            educational_box("Market Sentiment", "How people FEEL about the stock based on current news and social trends.")
            educational_box("Blue Chip Stocks", "Large, well-established companies with a history of reliable performance (like Reliance or Apple).")
        if st.button("Close Hub"):
            st.session_state.show_edu = False
            st.rerun()
