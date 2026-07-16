import streamlit as st
from supabase import create_client, Client
import pandas as pd
import yfinance as yf
import os
from dotenv import load_dotenv
load_dotenv()  
sb_url: str = os.getenv("sb_url")
sb_key: str = os.getenv("sb_key")
supabase: Client = create_client(sb_url,sb_key)

st.header("search for real value of your stock")
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
  
stock_options_num1 = search_list()

if 'stock_status_num1' not in st.session_state:
    st.session_state.stock_status_num1 = {}


select_stock_num1 = st.selectbox(
    "search for stock",options=[""]+stock_options_num1,index=0,key="568"
)
if select_stock_num1 != "":
    ticker_symbol_num1 = select_stock_num1.split("|")[0]
    name_num1 = select_stock_num1.split("|")[1]
    st.session_state.choose_stock_num1 = ticker_symbol_num1

    
    
def cally(ticker_symbol_num1):
  st.write(ticker_symbol_num1)
  ticker_object = yf.Ticker(ticker_symbol_num1)
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
  st.write(f"real price of {ticker_symbol_num1} : {real_price}")
  gap_sell_price = real_price * 0.3
  sell_price = gap_sell_price + real_price
  st.write(f"sell price of {ticker_symbol_num1} : {sell_price}")
  return 0
if st.button("search!",key="click90"):
  if st.session_state.choose_stock_num1:
    cally(ticker_symbol_num1)

def get_valid_token():
                    try:
                        supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
                        supabase.auth.get_user() 
                        return st.session_state.access_token
                    except:
                        try:
                            refresh_res = supabase.auth.refresh_session(st.session_state.refresh_token)
                            st.session_state.access_token = refresh_res.session.access_token
                            st.session_state.refresh_token = refresh_res.session.refresh_token
                            return st.session_state.access_token
                        except:
                               st.error("Session ของคุณหมดอายุแล้ว กรุณาล็อกอินใหม่")
                               return None
                             
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
    "search for stock",options=[""]+stock_options,index=0,key="569"
)
if select_stock != "":
    ticker = select_stock.split("|")[0]
    name = select_stock.split("|")[1]
    col1,col2 = st.columns([1,2])
    # ส่งคำสั่งไปถามฐานข้อมูล

    with col1:
        st.write(f"select stock:**{select_stock}**")
    with col2:
        valid_token = get_valid_token()
        if valid_token:
            current_user_uuid = st.session_state.user_id
            ticker_exist = supabase.table("stock_list") \
                .select("key_ticker") \
                .eq("key_ticker", ticker) \
                .eq("user_id", current_user_uuid) \
                .execute()
    
        is_added = st.session_state.stock_status.get(ticker, False)
        label = "delete" if ticker_exist.data  else "add"
        button_type = "primary" if ticker_exist.data  else "secondary"
    if select_stock !="":
        ticker = select_stock.split("|")[0]
        name = select_stock.split("|")[1]
        b = st.button(label, key=f"btn_{ticker}", type=button_type)
        thy_ticker = yf.Ticker(ticker)
        quarterly = thy_ticker.quarterly_financials
        latest_quarterly = quarterly.columns[0]
        u_lastest_quarterly = latest_quarterly.strftime('%Y-%m-%d')
        if b:
            st.session_state.stock_status[ticker] = not is_added
            if st.session_state.is_authenticated:
                valid_token = get_valid_token()
                if valid_token:
                    current_user_uuid = st.session_state.user_id
                    if not is_added:
                        your_stock = {
                            "key_ticker" : ticker,
                            "key_latest_quarterly" : u_lastest_quarterly,
                            "key_name" : name,
                            "user_id": current_user_uuid,
                        
                            }
                        supabase.postgrest.auth(valid_token)
                        supabase.table("stock_list").upsert(your_stock).execute()
                    else:
                        supabase.postgrest.auth(valid_token)
                        supabase.table("stock_list").delete().eq("key_ticker", ticker).eq("user_id", current_user_uuid).execute()             
                    st.rerun() 
                              
