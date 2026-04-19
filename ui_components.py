import streamlit as st

def metric_card(label, value, delta=None, delta_color="normal", help_text=None):
    """Custom styled metric card with glassmorphism."""
    delta_class = "delta-up" if delta and "+" in str(delta) else "delta-down" if delta and "-" in str(delta) else ""
    
    html = f"""
    <div class="st-key-metric-card" style="margin-bottom: 1rem;">
        <div class="metric-label">{label} {'ℹ️' if help_text else ''}</div>
        <div class="metric-value">{value}</div>
        {f'<div class="metric-delta {delta_class}">{delta}</div>' if delta else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    if help_text:
        st.caption(f"💡 {help_text}")

def beginner_badge(level):
    """Badge indicating if a stock is good for beginners."""
    if level == "Yes":
        st.success("✅ Good for Beginners (High Stability)")
    elif "No" in level:
        st.warning("⚠️ High Volatility (Advanced Traders Only)")
    else:
        st.info("ℹ️ Mixed Stability")

def section_header(title, subtitle=None):
    """Premium section header."""
    st.markdown(f"### {title}")
    if subtitle:
        st.markdown(f"<p style='color: #6C757D; margin-top: -10px; margin-bottom: 20px;'>{subtitle}</p>", unsafe_allow_html=True)

def educational_box(title, text):
    """Informative box for beginners."""
    st.markdown(f"""
    <div class="beginner-guide-box">
        <strong>📚 {title}</strong><br>
        <span style="font-size: 0.9rem;">{text}</span>
    </div>
    """, unsafe_allow_html=True)

def incident_card(title, source, time, description):
    """High-impact news card."""
    with st.container():
        st.markdown(f"""
        <div style="background: rgba(220, 53, 69, 0.05); border-left: 4px solid #DC3545; padding: 12px; border-radius: 4px; margin-bottom: 10px;">
            <p style="margin: 0; font-size: 0.8rem; color: #6C757D;">{source} • {time}</p>
            <p style="margin: 4px 0; font-weight: 700; color: #212529;">{title}</p>
            <p style="margin: 0; font-size: 0.85rem; color: #495057;">{description}</p>
        </div>
        """, unsafe_allow_html=True)

def macro_header(label, value, change):
    """Small clean header for macro tickers in sidebar."""
    color = "#28A745" if change > 0 else "#DC3545"
    st.markdown(f"""
    <div style="margin-bottom: 8px;">
        <span style="font-size: 0.8rem; color: #6C757D;">{label}</span><br>
        <span style="font-weight: 700; color: #212529;">{value}</span> 
        <span style="color: {color}; font-size: 0.75rem;">({change:+.2f}%)</span>
    </div>
    """, unsafe_allow_html=True)

def advice_badge(action, color):
    """Small badge for portfolio advice."""
    colors = {
        "green": "background-color: rgba(40, 167, 69, 0.1); color: #28A745; border: 1px solid #28A745;",
        "red": "background-color: rgba(220, 53, 69, 0.1); color: #DC3545; border: 1px solid #DC3545;",
        "yellow": "background-color: rgba(255, 193, 7, 0.1); color: #856404; border: 1px solid #FFEEBA;",
        "white": "background-color: #F8F9FA; color: #212529; border: 1px solid #DEE2E6;",
        "gray": "background-color: #E9ECEF; color: #495057; border: 1px solid #CED4DA;"
    }
    style = colors.get(color, colors["white"])
    return f'<span style="padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; {style}">{action}</span>'

def privacy_mask(value, is_masked, is_currency=True):
    """Hide sensitive numbers if privacy mode is on."""
    if is_masked:
        return "****"
    if isinstance(value, str):
        return value
    return f"₹{value:,.2f}" if is_currency else f"{value:,.2f}"

def groww_export_guide():
    """UI helper to guide user through Groww export."""
    st.markdown("""
    <div style="background: rgba(0, 123, 255, 0.05); border: 1px dashed #007BFF; padding: 15px; border-radius: 8px;">
        <h4 style="margin-top: 0; color: #007BFF;">📄 How to export from Groww</h4>
        <ol style="font-size: 0.85rem; color: #6C757D;">
            <li>Open the <b>Groww App</b> or Website.</li>
            <li>Go to <b>Profile</b> (top right) -> <b>Reports</b>.</li>
            <li>Select <b>Stocks</b> and then choose <b>Holdings Report</b>.</li>
            <li>Download as <b>CSV</b> or <b>Excel</b>.</li>
            <li>Upload the file here to sync your portfolio!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

def budget_stock_card(name, ticker, price, change):
    """Small card for budget-friendly recommendations."""
    color = "#28A745" if change >= 0 else "#DC3545"
    st.markdown(f"""
    <div style="background: #F8F9FA; padding: 12px; border-radius: 8px; border-left: 3px solid #007BFF; margin-bottom: 10px; border-top: 1px solid #DEE2E6; border-right: 1px solid #DEE2E6; border-bottom: 1px solid #DEE2E6;">
        <div style="font-size: 0.75rem; color: #6C757D;">{ticker}</div>
        <div style="font-weight: 700; font-size: 1rem; color: #212529;">{name}</div>
        <div style="font-size: 0.9rem; color: #212529;">₹{price:,.2f} <span style="color: {color}; font-size: 0.8rem;">({change:+.2f}%)</span></div>
    </div>
    """, unsafe_allow_html=True)

def impact_news_card(title, source, ticker, interpretation, color_code):
    """News card with AI impact footer."""
    style_map = {
        "green": "border-left: 4px solid #28A745; background: rgba(40, 167, 69, 0.05);",
        "red": "border-left: 4px solid #DC3545; background: rgba(220, 53, 69, 0.05);",
        "gray": "border-left: 4px solid #6C757D; background: rgba(108, 117, 125, 0.05);"
    }
    style = style_map.get(color_code, style_map["gray"])
    
    st.markdown(f"""
    <div style="{style} padding: 12px; border-radius: 4px; margin-bottom: 12px; border-top: 1px solid rgba(0,0,0,0.05); border-right: 1px solid rgba(0,0,0,0.05); border-bottom: 1px solid rgba(0,0,0,0.05);">
        <p style="margin: 0; font-size: 0.75rem; color: #6C757D;">{source} • Tagged: {ticker}</p>
        <p style="margin: 5px 0; font-weight: 500; font-size: 0.95rem; color: #212529;">{title}</p>
        <div style="margin-top: 8px; font-size: 0.8rem; font-style: italic; color: #495057;">
            🧬 AI Analysis: {interpretation}
        </div>
    </div>
    """, unsafe_allow_html=True)

def bargain_alert_card(name, ticker, current, low, dist_low, discount):
    """Card showing a stock near its yearly low."""
    st.markdown(f"""
    <div style="background: rgba(0, 123, 255, 0.05); border: 1px solid #007BFF; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <span style="font-size: 0.75rem; color: #6C757D;">{ticker} • BARGAIN ALERT</span>
                <h4 style="margin: 0; color: #212529;">{name}</h4>
            </div>
            <div style="text-align: right;">
                <span style="background: #007BFF; color: #FFFFFF; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">
                    {discount:.1f}% OFF HIGH
                </span>
            </div>
        </div>
        <div style="margin-top: 10px;">
            <div style="font-size: 0.85rem; color: #495057;">Current: ₹{current:,.2f} | 52W Low: ₹{low:,.2f}</div>
            <div style="font-size: 0.9rem; font-weight: 600; color: #28A745; margin-top: 4px;">
                🎯 Only {dist_low:.1f}% above yearly bottom!
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def load_local_css(file_name):
    """Load custom CSS."""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
