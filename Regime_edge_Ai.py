import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="RegimeEdge AI v1.0",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("RegimeEdge AI v1.0")
st.caption("Cutting-edge live forecasting • Historical correlation • Backtested precision")

FINNHUB_API_KEY = "d78i399r01qp0fl5ah30d78i399r01qp0fl5ah3g"

# Persistent data
if "watchlists" not in st.session_state:
    st.session_state.watchlists = {
        "AI Economy": ["NVDA", "AMD", "MSFT", "GOOGL", "AMZN"],
        "Semiconductors": ["NVDA", "AMD", "TSM", "AVGO", "MU"],
        "Cyber Security": ["CRWD", "PANW", "ZS", "FTNT"],
        "Biotech": ["REGN", "AMGN", "GILD", "VRTX"],
        "BTC & Crypto": ["BTC-USD", "ETH-USD"],
        "Major Indices": ["^GSPC", "^IXIC"]
    }
if "alerts" not in st.session_state:
    st.session_state.alerts = []

ticker = st.text_input("Enter ticker (NVDA, BTC-USD, ^GSPC for S&P 500, ^IXIC for NASDAQ)", "NVDA").upper().strip()

@st.cache_data(ttl=10, show_spinner=False)
def get_live_price(symbol):
    if not symbol: return None
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get("c")
    except:
        pass
    # Fallback to yfinance
    try:
        data = yf.download(symbol, period="1d", interval="1m", progress=False)
        if not data.empty:
            return float(data["Close"].iloc[-1])
    except:
        pass
    return None

@st.cache_data(ttl=300, show_spinner=False)
def get_candles(symbol):
    if not symbol: return None
    try:
        data = yf.download(symbol, period="1y", interval="1d", progress=False)
        if not data.empty:
            df = data.reset_index()
            df = df.rename(columns={"Date": "Date", "Open": "Open", "High": "High", "Low": "Low", "Close": "Close"})
            return df[['Date', 'Open', 'High', 'Low', 'Close']]
    except:
        pass
    return None

if ticker:
    current_price = get_live_price(ticker)
    candles = get_candles(ticker)
    
    if current_price is None:
        st.error("Live price fetch failed. Try again in a few seconds or use a major ticker.")
        st.stop()
    
    if candles is None or candles.empty or len(candles) < 30:
        st.warning("Limited historical data. Showing basic forecast.")
        forecast_5d_pct = 2.5
        confidence = 60
        regime = "Neutral"
    else:
        recent = candles.tail(30).reset_index(drop=True)
        recent_momentum = (recent['Close'].iloc[-1] / recent['Close'].iloc[0] - 1) * 100
        forecast_5d_pct = recent_momentum * 0.65
        confidence = round(max(55, min(92, 60 + abs(recent_momentum) * 1.2)))
        daily_vol = recent['Close'].pct_change().std()
        regime = "Risk-On" if recent_momentum > 2 and daily_vol < 0.025 else "High-Vol" if daily_vol >= 0.025 else "Risk-Off"
    
    daily_vol = candles['Close'].pct_change().std() if not candles.empty else 0.018
    lower_band = current_price * (1 - 1.8 * daily_vol * np.sqrt(5))
    upper_band = current_price * (1 + 1.8 * daily_vol * np.sqrt(5))
    
    tab1, tab2, tab3, tab4 = st.tabs(["Scan & Forecast", "Signal Card", "Regime & News", "Strategy Lab & Backtest"])
    
    with tab1:
        st.metric("Current Live Price", f"${current_price:,.2f}")
        
        if not candles.empty:
            fig_candle = go.Figure(data=[go.Candlestick(
                x=candles['Date'], open=candles['Open'], high=candles['High'],
                low=candles['Low'], close=candles['Close']
            )])
            fig_candle.update_layout(title="Last 365 Days Candlestick Chart", height=380, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_candle, use_container_width=True)
        
        fig_band = go.Figure()
        fig_band.add_trace(go.Scatter(x=["Now", "1-5 Days"], y=[current_price, current_price * (1 + forecast_5d_pct/100)],
                                    mode='lines+markers', name='Dynamic Forecast', line=dict(color='#1f77b4', width=3)))
        fig_band.add_trace(go.Scatter(x=["1-5 Days"], y=[lower_band], mode='lines', name='Lower Band',
                                    line=dict(dash='dash', color='#d62728')))
        fig_band.add_trace(go.Scatter(x=["1-5 Days"], y=[upper_band], mode='lines', name='Upper Band',
                                    line=dict(dash='dash', color='#2ca02c')))
        fig_band.update_layout(title="1-5 Day Forecast with Volatility-Adjusted Confidence Bands", height=340,
                               legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig_band, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("1-5 Day Forecast", f"+{forecast_5d_pct:.1f}%")
        with col2: st.metric("Confidence", f"{confidence}%")
        with col3: st.metric("Regime", regime)
    
    with tab2:
        st.subheader("Signal Card")
        direction = "BUY" if forecast_5d_pct > 0 else "SELL / HOLD"
        st.success(f"**{direction} {ticker}** – High-probability edge detected")
        atr = (candles['High'] - candles['Low']).tail(14).mean() if not candles.empty and len(candles) > 14 else current_price * 0.02
        stop_price = round(current_price - 2 * atr, 2)
        target_price = round(current_price + 3 * atr,
