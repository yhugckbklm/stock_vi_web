import edgar
edgar.set_identity("nihilis44@gmail.com")
import streamlit as st
company = edgar.Company("APPL")
financials = company.get_financials()

# ดึงค่าเดี่ยว (Scalar) ออกมาตรงๆ ไม่มีวันพลาด
net_income_this_year = financials.get_net_income()
total_assets = financials.get_total_assets()
st.write(net_income_this_year)