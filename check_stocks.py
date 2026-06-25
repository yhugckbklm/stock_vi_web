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

forward_pe = ticker_object.info.get('forwardPE')
peg_ratio = ticker_object.info.get('pegRatio')

if forward_pe and peg_ratio and peg_ratio != 0:
    g_from_peg = (forward_pe / peg_ratio)  # ผลลัพธ์มักออกมาเป็นเปอร์เซ็นต์เต็ม เช่น 14.5 หมายถึง 14.5%
    st.write(f"ค่า g (Analyst Growth) ที่ถอดจากค่า PEG ของระบบ: {g_from_peg:.2f}%")
    g_short = (g_from_peg / 100)
fcf_list = []    
pv_list = []    
h = (1 + 0.08)       
current_fcf = fcf
for year in range(1, 6):# คูณ FCF ของปีนี้ ด้วย (1 + g_short) เพื่อหา FCF ปีถัดไป
        next_fcf = current_fcf * (1 + g_short)
        current_fcf = next_fcf # อัปเดตตัวแปรเพื่อใช้คูณในลูปปีถัดไป
        fcf_list.append(current_fcf)
        pv = next_fcf/h**year
        pv_list.append(pv)
        st.write(f"fff{pv}")
total_one_pv = 0        
for o_pv in pv_list:
    one_pv = o_pv
    st.write(one_pv)  
    total_one_pv += one_pv
    st.write(total_one_pv)       

b_tv = fcf_list[4] * (1 + 0.2)/(0.08 - 0.02)
tv = b_tv/(1 + 0.08)**5
business_value = total_one_pv + tv
balance_sheet = ticker_object.balancesheet
total_debt = balance_sheet.loc['Total Debt'].iloc[0]
cash_and_equiv = balance_sheet.loc['Cash And Cash Equivalents'].iloc[0]
net_debt = total_debt - cash_and_equiv
equity_value = business_value - net_debt
total_shares = ticker_object.info.get('sharesOutstanding')
real_price = equity_value/total_shares
st.write(real_price)
