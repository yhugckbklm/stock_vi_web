import streamlit as st
import requests
import re
from supabase import create_client, Client
import pandas as pd
import yfinance as yf 
sb_url: str = "https://mmczveoapjucozahhohr.supabase.co"
sb_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1tY3p2ZW9hcGp1Y296YWhob2hyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU3OTgyODIsImV4cCI6MjA5MTM3NDI4Mn0.ZO6gqxInZEQD9xczdbzFMoWSKEQW8Wy1BoO54b3K0V8"
supabase: Client = create_client(sb_url,sb_key)


    
     
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
    
st.title("Why premium")

st.header("notification true value of your chosen stock every quarter.")
st.text("if you use the premium option, we will send you the true value of your chosen stock every quarter.")

st.header("if you are interested in premium option")

st.button("pay for premium quality")

st.title("premium")

     
                    
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
    st.session_state.user_email = ""
email = st.text_input("email:")
password = st.text_input("password:")
line_id = st.text_input("line id: ")

def signup(email, password):
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_pattern, email):
        return False
    if len(password) < 8:
        return False
    return True
s = st.button("sent")

if s:
    if signup(email, password):
        try:
            try:
                supabase.auth.sign_up({
                         "email":email,
                         "password":password
                         })
            except:
                pass
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
                })
            
            if response:
                st.session_state.access_token = response.session.access_token
                st.session_state.refresh_token = response.session.refresh_token
                st.session_state.user_id = response.user.id
                st.session_state.is_authenticated = True
                st.session_state.user_email = response.user.email
                st.success(f"ตอนนี้คุณล็อกอินในชื่อ: {response.user.email}")
                if st.session_state.is_authenticated:
                    st.rerun()      
        except Exception as e:
                     st.error(f" {str(e)}")

else:                     
    # ลิงก์ตรงจาก Nasdaq Trader (อัปเดตทุกวัน)
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
                            "user_id": current_user_uuid
                            
                            }
                        supabase.postgrest.auth(valid_token)
                        supabase.table("stock_list").upsert(your_stock).execute()
                    else:
                        supabase.postgrest.auth(valid_token)
                        supabase.table("stock_list").delete().eq("key_ticker", ticker).eq("user_id", current_user_uuid).execute()             
                    st.rerun() 
                              
