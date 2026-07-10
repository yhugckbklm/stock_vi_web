import streamlit as st
import yfinance as yf
import pandas as pd



st.header("real value of your stock")
ticker_symbol = st.session_state.selected_item

def cally(ticker_symbol):
  st.write(ticker_symbol)
  ticker_object = yf.Ticker(ticker_symbol)
  cash_flow = ticker_object.cashflow
  
  
  
  ##years_available = min(3, len(cash_flow.columns))
  
  ##cfo_series = cash_flow.loc['Operating Cash Flow'].iloc[0:years_available]
  ##normalized_cfo = cfo_series.mean()
  
  ##capex_series = cash_flow.loc['Capital Expenditure'].iloc[0:years_available].abs()
  ##normalized_capex = capex_series.mean()
  cfo = cash_flow.loc['Operating Cash Flow'].iloc[0]
# ดึงค่า CFO (Operating Cash Flow) และ CAPEX (Capital Expenditures)
# หมายเหตุ: ใน yfinance เวอร์ชันล่าสุด บรรทัดแถวจะถูกเก็บไว้เป็นชื่อเต็ม หรือใช้ .loc ในการดึง

  whole_capex = abs(cash_flow.loc['Capital Expenditure'].iloc[0])
  dna = cash_flow.loc['Depreciation And Amortization'].iloc[0]
  growth_capex = whole_capex - dna
  capex = whole_capex - growth_capex# 2. ดึงงบกระแสเงินสด (Cash Flow Statement) ออกมาเป็น DataFrame
  fcf = cfo - capex
  esti = ticker_object.get_growth_estimates()
  st.write(esti)
  g = esti.loc['+1y', 'stockTrend']
  st.write(g)
# 2. ดึงงบกระแสเงินสด (Cash Flow Statement) ออกมาเป็น DataFrame



  info = ticker_object.info
  balance_sheet = ticker_object.balancesheet
 

  
##cost_of_debt = 0.058    
##risk_free_rate = 0.035
##credit_spread = 0.020 # สมมติฐานส่วนต่างความเสี่ยงหนี้ 2.0%
##equity_risk_premium = 0.055
##corporate_tax_rate = 0.21

##try:
    ##short_debt = ticker_object.balancesheet.loc['Current Debt'].iloc[0]
##except:
    ##short_debt = 0    
##long_debt = ticker_object.balancesheet.loc['Long Term Debt'].iloc[0]
##total_debt = short_debt + long_debt
##beta = ticker_object.info.get('beta')
##market_cap = ticker_object.info.get('marketCap')

##total_value = market_cap + total_debt
##weight_of_debt = total_debt / total_value
##weight_of_equity = market_cap / total_value
##cost_of_debt = risk_free_rate + credit_spread
##cost_of_equity = risk_free_rate + (beta * equity_risk_premium)
##wacc = (weight_of_equity * cost_of_equity) + (weight_of_debt * cost_of_debt * (1 - corporate_tax_rate))
  fcf_list = []    
  pv_list = []
  wacc = 0.08    
  h = (1 + wacc)       
  current_fcf = fcf
  for year in range(1, 6):# คูณ FCF ของปีนี้ ด้วย (1 + g_short) เพื่อหา FCF ปีถัดไป
    next_fcf = current_fcf * (1 + g)
    current_fcf = next_fcf # อัปเดตตัวแปรเพื่อใช้คูณในลูปปีถัดไป
    fcf_list.append(current_fcf)
    pv = next_fcf/(h)**year
    pv_list.append(pv)
        ##st.write(f"fff{pv}")
  total_one_pv = 0        
  for o_pv in pv_list:
    one_pv = o_pv
    ##st.write(one_pv)  
    total_one_pv += one_pv
    ##st.write(total_one_pv)       

  b_tv = fcf_list[4] * (1 + 0.03)/(wacc - 0.03)
  tv = b_tv/(h)**5
  business_value = total_one_pv + tv
  
  total_debt = balance_sheet.loc['Total Debt'].iloc[0]
  cash_and_equiv = balance_sheet.loc['Cash And Cash Equivalents'].iloc[0]
  net_debt = total_debt - cash_and_equiv
  equity_value = business_value - net_debt
  total_shares = info.get('sharesOutstanding')
  real_price = equity_value/total_shares
  st.write(f"real price of {ticker_symbol} : {real_price}")
  gap_sell_price = real_price * 0.3
  sell_price = gap_sell_price + real_price
  st.write(f"sell price of {ticker_symbol} : {sell_price}")
  return 0
cally(ticker_symbol)  
