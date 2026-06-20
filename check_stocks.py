import streamlit as st
import yfinance as yf
import pandas as pd
from edgar import Company, set_identity
set_identity("nihilis44@gmail.com")
from edgar.xbrl import XBRL

st.header("Welcome to Premium")
ticker_symbol = st.session_state.selected_item
st.write(ticker_symbol)

def calculate(ticker_symbol):
    score_collect = []
    
    if not ticker_symbol:
        return score_collect
        
    try:
        # 1. ดึงข้อมูลจาก edgartools
        company = Company(ticker_symbol)
        financials = company.get_financials()
        stock_revenue = financials.income_statement()
        df = stock_revenue.to_dataframe(view="standard")
        # ขั้นที่ 1: หาว่าคอลัมน์ไหนในตารางคือคอลัมน์ "concept"
        concept_col = None
        for col in df.columns:
            if "concept" in col.lower():
                concept_col = col
                break
        
        if concept_col is None:
            st.warning(f"{ticker_symbol}: ไม่เจอคอลัมน์ concept เลย")    
        
        df["clean_concept"] = df[concept_col].astype(str).str.lower().str.strip()  
        target_keywords = [
            "revenue",
            "total revenue",
            "total sales",
            "net sales",
            "sales revenue",
            "operating revenue"
        ]
        # ขั้นที่ 2: กรองแถวที่ concept ตรงกับ Revenue
        for keyword in target_keywords:
            revenue_row = df[df["clean_concept"].str.contains(keyword, na=False)]
            # ขั้นที่ 3: ดึงค่าตัวเลขออกมา
            if not revenue_row.empty:
                numeric_cols = df.select_dtypes(include="number").columns
                revenue_value = revenue_row.iloc[0][numeric_cols[0]]
                st.write("Revenue:", revenue_value)
            else:
                st.write("ไม่เจอ concept Revenue ในตารางนี้")
        return score_collect
    except Exception as e:
        st.error(f"ไม่สามารถดึงข้อมูล SEC สำหรับหุ้น {ticker_symbol} ได้: {e}")
        return score_collect
calculate(ticker_symbol)
   