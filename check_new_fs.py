import yfinance as yf
from supabase import create_client, Client

sb_url: str = "https://mmczveoapjucozahhohr.supabase.co"
sb_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1tY3p2ZW9hcGp1Y296YWhob2hyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTc5ODI4MiwiZXhwIjoyMDkxMzc0MjgyfQ.BVchJwn-sMJmA32YmQ8VhCOWAZnNRiL1pkBx7n9rNNA"
supabase: Client = create_client(sb_url,sb_key)

u_stocks = supabase.table("stock_list").select("key_ticker").execute()


print(u_stocks)
ticker_list = []

for stock in u_stocks.data:
    ticker = (stock['key_ticker'])
    ticker_list.append(ticker)
for i in ticker_list:
    date = supabase.table("stock_list").select("latest_quarterly").eq("key_ticker", i).execute()
    u_date = date.data[0]['latest_quarterly']
    
    stock = yf.Ticker(i)
    quarterly = stock.quarterly_financials
    latest_quarterly = quarterly.columns[0]
    u_latest_quarterly = latest_quarterly.strftime('%Y-%m-%d')
    if u_date == latest_quarterly:
        u_iden = supabase.table("stock_list").select("user_id").eq("key_ticker", i).execute()
def bot_sent(target_line,f):
    url = ""
    headers = {
        head
    }
    data = {
        "to" : target_line,
        
        
    }
