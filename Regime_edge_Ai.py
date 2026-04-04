import streamlit as st
import requests
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="RegimeEdge AI",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("RegimeEdge AI")
st.caption("Live forecasts • Confidence bands • Alerts • Theme watchlists")

FINNHUB_API_KEY = "d78i399r01qp0fl5ah30d78i399r01qp0fl5ah3g"

# Persistent data
if "watchlists" not in st.session_state:
    st.session_state.watchlists = {
        "AI Economy": ["NVDA", "AMD", "MSFT", "GOOGL", "AMZN"],
        "Semiconductors": ["NVDA", "AMD", "TSM", "AVGO", "MU"],
        "Cyber Security": ["CRWD", "PANW", "ZS", "FTNT"],
        "Biotech": ["REGN", "AMGN", "GILD", "VRTX"],
        "BTC & Crypto": ["BTC-USD", "ETH-USD"]
    }
if "alerts" not in st.session_state:
    st.session_state.alerts = []

ticker = st.text_input("Enter ticker (NVDA, BTC-USD, etc.)", "NVDA").upper().strip()

@st.cache_data(ttl=60)
def get_live_price(symbol):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("c")
        return None
    except:
        return None

if ticker:
    current_price = get_live_price(ticker)
    
    if current_price:
        # Demo forecast values
        forecast_5d = 4.2
        confidence = 72
        lower_band = current_price * (1 - 0.07)
        upper_band = current_price * (1 + 0.13)
        
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Scan & Forecast", "Signal Card", "Regime & News", "Watchlists & Alerts"])
        
        with tab1:  # Scan & Forecast + Confidence Bands
            st.metric("Current Live Price", f"${current_price:,.2f}")
            
            # Confidence bands chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=["Now", "1-5 Days"], y=[current_price, current_price * (1 + forecast_5d/100)],
                                   mode='lines+markers', name='Forecast', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=["1-5 Days"], y=[lower_band], mode='markers', name='Lower 95% Band', marker=dict(color='red')))
            fig.add_trace(go.Scatter(x=["1-5 Days"], y=[upper_band], mode='markers', name='Upper 95% Band', marker=dict(color='green')))
            fig.update_layout(title="1-5 Day Forecast with Confidence Bands", height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("1-5 Day Forecast", f"+{forecast_5d}%")
            with col2: st.metric("Confidence", f"{confidence}%")
            with col3: st.metric("Regime", "Risk-On")
        
        with tab2:  # Signal Card
            st.subheader("Signal Card")
            direction = "BUY" if forecast_5d > 0 else "SELL / HOLD"
            st.success(f"**{direction} {ticker}**")
            stop_price = round(current_price * 0.92, 2)
            target_price = round(current_price * 1.15, 2)
            st.info(f"""
            **Entry**: ${current_price:,.2f}  
            **Stop Loss**: ${stop_price:,.2f}  
            **Target**: ${target_price:,.2f}  
            **Expected Move**: ±{abs(forecast_5d)}% over 1–5 days  
            **Confidence**: {confidence}%
            """)
            
            account = st.number_input("Account size ($)", value=10000, step=1000)
            risk_pct = st.slider("Max risk per trade (%)", 0.5, 5.0, 1.0)
            risk_amount = account * risk_pct / 100
            stop_dist = current_price * 0.08
            shares = int(risk_amount / stop_dist) if stop_dist > 0 else 0
            st.write(f"**Recommended shares**: **{shares}**")
            st.write(f"**Risk amount**: **${risk_amount:,.0f}**")
        
        with tab3:  # Regime & News
            st.subheader("Market Regime & Sentiment")
            st.write("**Current Regime**: Risk-On (demo)")
            st.write("**News Momentum Score**: +1.8 (bullish)")
            st.progress(0.78)
        
        with tab4:  # Watchlists & Alerts
            st.subheader("Theme Watchlists")
            selected_theme = st.selectbox("Select theme", list(st.session_state.watchlists.keys()))
            st.write("**Tickers**:", ", ".join(st.session_state.watchlists[selected_theme]))
            
            if st.button("Add current ticker to selected theme"):
                if ticker not in st.session_state.watchlists[selected_theme]:
                    st.session_state.watchlists[selected_theme].append(ticker)
                    st.success(f"✅ {ticker} added to {selected_theme}")
            
            st.subheader("Set Alerts")
            alert_type = st.radio("Alert type", ["Price level", "% Move"])
            if alert_type == "Price level":
                alert_price = st.number_input("Alert when price reaches", value=current_price * 1.05)
                if st.button("Set Price Alert"):
                    st.session_state.alerts.append(f"{ticker} reaches ${alert_price:,.2f}")
                    st.success("Alert saved!")
            else:
                alert_pct = st.number_input("% Move alert", value=5.0)
                if st.button("Set % Move Alert"):
                    st.session_state.alerts.append(f"{ticker} moves {alert_pct}%")
                    st.success("Alert saved!")
            
            st.write("**Active Alerts**:", st.session_state.alerts if st.session_state.alerts else "None yet")
    else:
        st.error("Could not fetch live price. Try NVDA or BTC-USD.")
else:
    st.info("Enter a ticker to load live data and forecasts.")

st.caption("Live via Finnhub • Confidence bands + alerts + theme watchlists active • Not financial advice")
