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
   
                
