import streamlit as st
import pandas as pd
import yfinance as yf
import ta

def fetch_data(symbol, period="6mo", interval="1d"):
    try:
        df = yf.download(symbol, period=period, interval=interval)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        return None

def analyze_stock(df):
    close = df['Close']
    volume = df['Volume']

    # Technical Indicators
    df['EMA_10'] = ta.trend.ema_indicator(close, window=10)
    df['EMA_20'] = ta.trend.ema_indicator(close, window=20)
    df['EMA_50'] = ta.trend.ema_indicator(close, window=50)
    df['EMA_100'] = ta.trend.ema_indicator(close, window=100)
    df['EMA_200'] = ta.trend.ema_indicator(close, window=200)
    df['MACD'] = ta.trend.macd(close)
    df['MACD_signal'] = ta.trend.macd_signal(close)
    df['RSI'] = ta.momentum.rsi(close)
    bb = ta.volatility.BollingerBands(close)
    df['BB_bbm'] = bb.bollinger_mavg()
    df['BB_bbh'] = bb.bollinger_hband()
    df['BB_bbl'] = bb.bollinger_lband()

    latest = df.iloc[-1]

    ema_tight = abs(latest['EMA_10'] - latest['EMA_200']) < latest['Close'] * 0.01
    macd_cross = latest['MACD'] > latest['MACD_signal']
    rsi_breakout = latest['RSI'] > 55
    bb_squeeze = (latest['BB_bbh'] - latest['BB_bbl']) / latest['BB_bbm'] < 0.05

    return ema_tight and macd_cross and rsi_breakout and bb_squeeze

st.set_page_config(page_title="Breakout Scanner", layout="centered")
st.title("🔥 Breakout-Ready Stock Scanner (EMA + Volume + MACD + RSI + BB Squeeze)")

symbols = st.text_area("Enter comma-separated NSE symbols (e.g., RELIANCE.NS, INFY.NS)",
                      value="RELIANCE.NS, TCS.NS, INFY.NS")

if symbols:
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    st.markdown("---")
    st.subheader("Scanner Output:")

    breakout_candidates = []

    for sym in symbol_list:
        try:
            df = fetch_data(sym)
            if df is not None:
                if analyze_stock(df):
                    breakout_candidates.append(sym)
            else:
                st.warning(f"{sym}: Failed to fetch data")
        except Exception as e:
            st.error(f"{sym}: Error - {e}")

    if breakout_candidates:
        st.success("\n".join(breakout_candidates))
    else:
        st.info("No breakout candidates found at the moment.")
