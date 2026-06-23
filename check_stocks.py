import streamlit as st
import yfinance as yf
import pandas as pd
from edgar import Company, set_identity

# ตั้งค่า Identity สำหรับดึงข้อมูล SEC
set_identity("nihilis44@gmail.com")


st.header("Welcome to Premium")
ticker_symbol = st.session_state.selected_item
st.write(ticker_symbol)
ticker_object = yf.Ticker(ticker_symbol)

# 2. ดึงงบกระแสเงินสด (Cash Flow Statement) ออกมาเป็น DataFrame
cash_flow = ticker_object.quarterly_cash_flow

# 3. เจาะจงดึงแถว CFO (ใน yfinance จะใช้ชื่อมาตรฐานว่า 'Operating Cash Flow')
# มันจะดึงข้อมูลย้อนหลังมาให้ 4 ปีล่าสุดทันที
cfo_data = cash_flow.loc['Operating Cash Flow'].iloc[:4]
p_cfo_data = cfo_data.sum()

st.write(p_cfo_data)


