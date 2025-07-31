import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="🔥 Breakout Scanner", layout="wide")
st.title("🔥 Breakout-Ready Stock Scanner (EMA + Volume + MACD + RSI + BB Squeeze)")

def is_ready_to_fire(df):
    df['EMA10'] = ta.trend.ema_indicator(df['Close'], window=10)
    df['EMA20'] = ta.trend.ema_indicator(df['Close'], window=20)
    df['EMA50'] = ta.trend.ema_indicator(df['Close'], window=50)
    df['EMA100'] = ta.trend.ema_indicator(df['Close'], window=100)
    df['EMA200'] = ta.trend.ema_indicator(df['Close'], window=200)

    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()

    df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()

    bb = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    df['BB_width'] = df['BB_upper'] - df['BB_lower']
    df['Volume_Avg10'] = df['Volume'].rolling(10).mean()

    last = df.iloc[-1]
    emas = [last['EMA10'], last['EMA20'], last['EMA50'], last['EMA100'], last['EMA200']]
    max_ema = max(emas)
    min_ema = min(emas)

    return all([
        (max_ema - min_ema) / min_ema < 0.02,
        abs(last['Close'] - last['EMA50']) / last['Close'] < 0.01,
        last['Volume'] > 1.5 * last['Volume_Avg10'],
        last['MACD'] > last['MACD_signal'],
        last['RSI'] > 55,
        last['BB_width'] < df['BB_width'].rolling(20).min().iloc[-1] * 1.1
    ])

# UI
stock_input = st.text_area("Enter comma-separated NSE symbols (e.g., RELIANCE.NS, INFY.NS)", value="RELIANCE.NS, TCS.NS, INFY.NS")
symbols = [x.strip() for x in stock_input.split(",") if x.strip()]
results = []

with st.spinner("Scanning..."):
    for symbol in symbols:
        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)
            if len(df) > 100 and is_ready_to_fire(df):
                results.append(symbol)
        except Exception as e:
            st.warning(f"{symbol}: Error - {e}")

if results:
    st.success("🔥 These stocks are ready to fire:")
    st.table(pd.DataFrame(results, columns=["Symbol"]))
else:
    st.info("No breakout candidates found at the moment.")
