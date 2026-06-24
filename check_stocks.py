import streamlit as st
import yfinance as yf
import pandas as pd



st.header("Welcome to Premium")
ticker_symbol = st.session_state.selected_item
st.write(ticker_symbol)
ticker_object = yf.Ticker(ticker_symbol)
cash_flow = ticker_object.cashflow

# ดึงค่า CFO (Operating Cash Flow) และ CAPEX (Capital Expenditures)
# หมายเหตุ: ใน yfinance เวอร์ชันล่าสุด บรรทัดแถวจะถูกเก็บไว้เป็นชื่อเต็ม หรือใช้ .loc ในการดึง
fcf = cash_flow.loc['Free Cash Flow'].iloc[0]
# 2. ดึงงบกระแสเงินสด (Cash Flow Statement) ออกมาเป็น DataFrame


st.write(fcf)



