import yfinance as yf
from supabase import create_client, Client
import requests
import streamlit as st
from datetime import date
import os
from dotenv import load_dotenv
load_dotenv()  
sb_url: str = os.getenv("sb_url")
sb_key: str = os.getenv("sb_secret")
supabase: Client = create_client(sb_url,sb_key)

u_stocks = supabase.table("stock_list").select("key_ticker", "key_latest_quarterly").execute()
print(u_stocks)
def bot_sent(target_line, message_text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer GbEzWTFiswsyh1hfCYbnJoiLxIxboE4HKsNkkaB5DwrDy43glRV9845KkZf4E74IiEuyCCDNKutoc3UTdjahGJDb9kzQHr82e9WZDrnxmiu58CqCqJf9r5hEE5oikqg/q55KBlqreGBN8IlheXbAxgdB04t89/1O/w1cDnyilFU=" # รหัสผ่านของบอทเรา
    }
    data = {
        "to" : target_line,
        "messages": [
            {
                "type": "text",
                "text": message_text
            }
        ]  
    }
    response = requests.post(url, headers=headers, json=data)




ticker_list = {}

for stock in u_stocks.data:
    ticker = stock['key_ticker']
    date = stock['key_latest_quarterly']
    ticker_list[ticker] = date
    stock = yf.Ticker(ticker)
    quarterly = stock.quarterly_financials
    latest_quarterly = quarterly.columns[0]
    u_latest_quarterly = latest_quarterly.strftime('%Y-%m-%d')
    print(u_latest_quarterly)
    if date != u_latest_quarterly:
        u_user = supabase.table("stock_list").select("user_id").eq("key_ticker", ticker).execute()
        for u in u_user.data:
            name_u_user = u['user_id']
            u_iden = supabase.table("user_info").select("line_id").eq("id", name_u_user).execute()
            if u_iden.data:
                for o in u_iden.data:
                    line_id = o['line_id']
                    line_message = f"{ticker} it's already new quarter check new value of your stocks"
                    bot_sent(line_id, line_message)

