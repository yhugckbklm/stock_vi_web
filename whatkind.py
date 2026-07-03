import streamlit as st
import yfinance as yf
import pandas as pd

st.header("Welcome to Premium")
url = "http://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt"

                      
                                
                           
try:
    # ต้องระบุ sep='|' เพราะไฟล์นี้ใช้ขีดตั้งเป็นตัวแบ่ง
    df = pd.read_csv(url, sep='|')
    
    # ลบบรรทัดสุดท้ายที่เป็นข้อความสรุป (มักจะทำให้เกิด Error ถ้าไม่ลบ)
    df = df[:-1] 
    
    # เลือกเฉพาะ Symbol และชื่อหุ้น (ในไฟล์นี้ใช้ชื่อ 'Symbol' และ 'Security Name')
    df_cleaned = df[['Symbol', 'Security Name']]
    
    # บันทึกเป็น CSV จริงๆ (ใช้คอมม่าปกติ)
    df_cleaned.to_csv("nasdaq_stocks.csv", index=False)
    print("ดาวน์โหลดและบันทึกไฟล์สำเร็จ!")
    
except Exception as e:
    print(f"เกิดข้อผิดพลาด: {e}")
       
@st.cache_data
def search_list():
    
    df = pd.read_csv("nasdaq_stocks.csv")
    df['display_text'] = df['Symbol']+"|"+df['Security Name']
    
    return df['display_text'].tolist()
  
stock_options = search_list()

if 'stock_status' not in st.session_state:
    st.session_state.stock_status = {}


select_stock = st.selectbox(
    "input stock",options=[""]+stock_options,index=0
)
if select_stock != "":
    ticker_symbol = select_stock.split("|")[0]
    name = select_stock.split("|")[1]
    st.session_state.choose_stock = ticker_symbol

    
    
def cally(ticker_symbol):
  st.write(ticker_symbol)
  ticker_object = yf.Ticker(ticker_symbol)
  cash_flow = ticker_object.cashflow
  cfo = cash_flow.loc['Operating Cash Flow'].iloc[0]
# ดึงค่า CFO (Operating Cash Flow) และ CAPEX (Capital Expenditures)
# หมายเหตุ: ใน yfinance เวอร์ชันล่าสุด บรรทัดแถวจะถูกเก็บไว้เป็นชื่อเต็ม หรือใช้ .loc ในการดึง
  whole_capex = cash_flow.loc['Capital Expenditure'].iloc[0]
  dna = cash_flow.loc['Depreciation And Amortization'].iloc[0]
  growth_capex = whole_capex - dna
  capex = whole_capex + growth_capex# 2. ดึงงบกระแสเงินสด (Cash Flow Statement) ออกมาเป็น DataFrame
  fcf = cfo - capex

##st.write(fcf)
  info = ticker_object.info
  forward_pe = info.get('forwardPE')
  peg_ratio = info.get('pegRatio')

  if forward_pe and peg_ratio and peg_ratio != 0:
    g_from_peg = (forward_pe / peg_ratio)  # ผลลัพธ์มักออกมาเป็นเปอร์เซ็นต์เต็ม เช่น 14.5 หมายถึง 14.5%
    ##st.write(f"ค่า g (Analyst Growth) ที่ถอดจากค่า PEG ของระบบ: {g_from_peg:.2f}%")
    g_short = (g_from_peg / 100)
   
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
  h = (1 + 0.08)       
  current_fcf = fcf
  for year in range(1, 6):# คูณ FCF ของปีนี้ ด้วย (1 + g_short) เพื่อหา FCF ปีถัดไป
    next_fcf = current_fcf * (1 + g_short)
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

  b_tv = fcf_list[4] * (1 + 0.03)/(0.08 - 0.03)
  tv = b_tv/(1 + 0.08)**5
  business_value = total_one_pv + tv
  balance_sheet = ticker_object.balancesheet
  total_debt = balance_sheet.loc['Total Debt'].iloc[0]
  cash_and_equiv = balance_sheet.loc['Cash And Cash Equivalents'].iloc[0]
  net_debt = total_debt - cash_and_equiv
  equity_value = business_value - net_debt
  total_shares = info.get('sharesOutstanding')
  real_price = equity_value/total_shares
  st.write(f"real price of {ticker_symbol} : {real_price}")
  return 0
if st.button("umm:",key="click90"):
  if st.session_state.choose_stock:
    cally(ticker_symbol)
