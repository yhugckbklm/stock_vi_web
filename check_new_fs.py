import yfinance as yf
from supabase import create_client, Client
import requests
import streamlit as st

sb_url: str = "https://mmczveoapjucozahhohr.supabase.co"
sb_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1tY3p2ZW9hcGp1Y296YWhob2hyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTc5ODI4MiwiZXhwIjoyMDkxMzc0MjgyfQ.BVchJwn-sMJmA32YmQ8VhCOWAZnNRiL1pkBx7n9rNNA"
supabase: Client = create_client(sb_url,sb_key)

u_stocks = supabase.table("stock_list").select("key_ticker").execute()

def bot_sent(target_line, message_text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "9a951114e10efa6a5a3f0187a56e14d6" # รหัสผ่านของบอทเรา
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
    requests.post(url,header=headers,json=data)



print(u_stocks)
ticker_list = []

for stock in u_stocks.data:
    ticker = (stock['key_ticker'])
    ticker_list.append(ticker)
for i in ticker_list:
    u_ticker = (i[ticker_list])
    date = supabase.table("stock_list").select("latest_quarterly").eq("key_ticker", u_ticker).execute()
    u_date = date.data[0]['latest_quarterly']
    
    stock = yf.Ticker(i)
    quarterly = stock.quarterly_financials
    latest_quarterly = quarterly.columns[0]
    u_latest_quarterly = latest_quarterly.strftime('%Y-%m-%d')
    if u_date == u_latest_quarterly:
        u_user = supabase.table("stock_list").select("user_id").eq("key_ticker", u_ticker).execute()
        for u in u_user.data:
            name_u_user = (u[u_user.data])
            u_iden = supabase.table("user_info").select("line_id").eq("id", name_u_user).execute()
        if u_iden.data:
            for o in u_iden.data:
                line_id = (o[u_iden.data])
                line_message = {
                    "key_message" : "it's already new quarter! check new value of your stocks"
                }
                bot_sent(line_id, line_message)
