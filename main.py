import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv
load_dotenv()  
sb_url: str = os.getenv("sb_url")
sb_key: str = os.getenv("sb_key")
supabase: Client = create_client(sb_url,sb_key)
# 1. จัดการ Session State
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'page_selection' not in st.session_state:
    st.session_state.page_selection = False


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


# 2. Sidebar (ปุ่มควบคุมจะมีแค่ที่ไฟล์นี้ที่เดียว)
with st.sidebar:
    col1, col2 = st.columns([3, 2])
    with col1:
        st.write("register page")
    with col2:
        if st.button("click!", key="btn2"):
            st.session_state.page_selection = "regis"
            st.rerun()
    col1, col2 = st.columns([3, 2])        
    with col1:
        st.write("home page")
    with col2:
        if st.button("click!", key="btn1"):
            st.session_state.page_selection = "home"
            st.rerun()
    if st.session_state.is_authenticated:
        valid_token = get_valid_token()
        if valid_token: 
            current_user_uuid = st.session_state.user_id  
            print((type(current_user_uuid)))                
            u_stocks = supabase.table("stock_list").select("key_ticker").eq("user_id",current_user_uuid).execute()    
            ticker_list = []
            for stock in u_stocks.data:
                ticker = stock['key_ticker']
                ticker_list.append(ticker)
            for i, item in enumerate(ticker_list):
                row_c1, row_c2 = st.columns([3, 2]) 
                with row_c1:
                    st.write(item)
                with row_c2:    
                    if st.button(f"see", key=f"btn{item}_{i}"):
                        st.session_state.selected_item = item
                        st.session_state.page_selection = "check_stocks"
                        st.rerun()                
    else:
        if not st.session_state.page_selection:
            st.session_state.page_selection = "regis"
                                            
# 3. เลือก Page
if st.session_state.page_selection == "regis":
    target_page = st.Page("regis1.py", title="Registration")
    pg = st.navigation([target_page])
    pg.run()
elif st.session_state.page_selection == "check_stocks":
    target_page = st.Page("check_stocks.py", title="your stock value")
    pg = st.navigation([target_page])
    pg.run()
elif st.session_state.page_selection == "home":
    target_page = st.Page("whatkind.py", title="stock value")
    pg = st.navigation([target_page])
    pg.run()
else:
    target_page = st.Page("whatkind.py", title="stock value") # เปลี่ยนชื่อไฟล์หน้า Home
    pg = st.navigation([target_page])
    pg.run()

