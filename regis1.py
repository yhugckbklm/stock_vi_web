import streamlit as st
import re
from supabase import create_client, Client
import pandas as pd
import yfinance as yf
import os
from dotenv import load_dotenv
load_dotenv()  
sb_url: str = os.getenv("sb_url")
sb_key: str = os.getenv("sb_key")
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
  
def signup(email, password, line_id):
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        lineid_pattern = r'^U[0-9a-f]{32}$'
        if not re.match(email_pattern, email):
            return False
        if len(password) < 8:
            return False
        if not re.match(lineid_pattern, line_id):
            return False
        return True
    
def signin(email_sign , password_sign):
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_pattern, email_sign):
            return False
        if len(password_sign) < 8:
            return False
        return True   
            

st.header("Welcome to Tech DCF")


    
                   
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
    st.session_state.user_email = ""
with st.form("my_signup_form"):
    st.header("sign up")
    email = st.text_input("email:",key="signup_email")
    password = st.text_input("password:",key="signup_password")
    raw_line_id = st.text_input("line id: ")
    line_id = str(raw_line_id)

    
 
    s = st.form_submit_button("sent")

if s:
    if signup(email, password, line_id):
        try:
            supabase.auth.sign_up({
                         "email" : email,
                         "password" : password,
                         "options":{
                             "data":{
                                 "line_id" : line_id
                             }
                         }
                })
        except Exception as e:
            st.error(f"สมัครสมาชิกไม่สำเร็จ: {e}")
                        
with st.form("my_signin_form"):
    st.header("sign in")
    email_sign = st.text_input("email:",key="login_email")
    password_sign = st.text_input("password:",key="login_pass")
            
    sign_in_button = st.form_submit_button("sent")

if sign_in_button:
    
    if signin(email_sign, password_sign):
        response = supabase.auth.sign_in_with_password({
                "email":email_sign,
                "password":password_sign
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
    "search for stock",options=[""]+stock_options,index=0
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
                              
