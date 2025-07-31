# streamlit_app.py
import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

def is_ready_to_fire(df):
    df['EMA10'] = ta.ema(df['Close'], 10)
    df['EMA20'] = ta.ema(df['Close'], 20)
    df['EMA50'] = ta.ema(df['Close'], 50)
    df['EMA100'] = ta.ema(df['Close'], 100)
    df['EMA200'] = ta.ema(df['Close'], 200)
    macd = ta.macd(df['Close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_signal'] = macd['MACDs_12_26_9']
    df['RSI'] = ta.rsi(df['Close'], 14)
    bb = ta.bbands(df['Close'], length=20)
    df['BB_upper'] = bb['BBU_20_2.0']
    df['BB_lower'] = bb['BBL_20_2.0']
    df['BB_width'] = df['BB_upper'] - df['BB_lower']
    df['VolAvg10'] = df['Volume'].rolling(10).mean()

    last = df.iloc[-1]
    emas = [last['EMA10'], last['EMA20'], last['EMA50'], last['EMA100'], last['EMA200']]
    max_ema = max(emas)
    min_ema = min(emas)

    return all([
        (max_ema - min_ema) / min_ema < 0.02,
        abs(last['Close'] - last['EMA50']) / last['Close'] < 0.01,
        last['Volume'] > 1.5 * last['VolAvg10'],
        last['MACD'] > last['MACD_signal'],
        last['RSI'] > 55,
        last['BB_width'] < df['BB_width'].rolling(20).min().iloc[-1] * 1.1
    ])

# --- Streamlit App ---
st.set_page_config(page_title="🔥 Breakout Scanner", layout="wide")
st.title("🔥 Breakout-Ready Stock Scanner (EMA + Volume + MACD + RSI + BB Squeeze)")

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
            st.warning(f"{symbol}: Failed to fetch or process. Error: {e}")

if results:
    st.success("🔥 These stocks are ready to fire:")
    st.table(pd.DataFrame(results, columns=["Symbol"]))
else:
    st.info("No breakout candidates found right now.")

