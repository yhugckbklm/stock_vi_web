import streamlit as st
import requests

st.header("Welcome to Premium (FMP Version)")

# ใส่ API Key ของ Financial Modeling Prep ตรงนี้
FMP_API_KEY = "YOUR_FMP_API_KEY"  

premium_user_stock = st.text_input("Input your stock symbol (e.g., AAPL): ").upper()

def get_fmp_data(ticker):
    """ฟังก์ชันสําหรับดึงข้อมูลจาก FMP API แยกตาม Endpoint"""
    data = {}
    try:
        # 1. ดึงข้อมูล Profile & Valuation Metrics อื่นๆ
        profile_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
        profile_res = requests.get(profile_url).json()
        if profile_res:
            data['profile'] = profile_res[0]
            
        # 2. ดึงข้อมูล Key Metrics (เช่น PBV, Payout Ratio, ROE)
        metrics_url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}?apikey={FMP_API_KEY}"
        metrics_res = requests.get(metrics_url).json()
        if metrics_res:
            data['metrics'] = metrics_res[0]
            
        # 3. ดึงงบกระแสเงินสด (Cash Flow Statement) ย้อนหลัง
        cf_url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?limit=5&apikey={FMP_API_KEY}"
        data['cashflow'] = requests.get(cf_url).json()
        
        # 4. ดึงงบดุล (Balance Sheet) รายไตรมาสล่าสุด
        bs_url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?period=quarter&limit=1&apikey={FMP_API_KEY}"
        bs_res = requests.get(bs_url).json()
        if bs_res:
            data['balance_sheet'] = bs_res[0]
            
        # 5. ดึงข้อมูลการเติบโต (Financial Growth)
        growth_url = f"https://financialmodelingprep.com/api/v3/financial-growth/{ticker}?limit=1&apikey={FMP_API_KEY}"
        growth_res = requests.get(growth_url).json()
        if growth_res:
            data['growth'] = growth_res[0]

    except Exception as e:
        st.error(f"Error fetching data from FMP: {e}")
    return data

def calculate_fmp(ticker_symbol):
    if not ticker_symbol:
        return []
        
    api_data = get_fmp_data(ticker_symbol)
    if 'profile' not in api_data:
        st.error("Stock symbol not found or API limit exceeded.")
        return []
        
    score_collect = []
    
    # ดึงตัวแปรพื้นฐานจาก Profile และ Metrics เพื่อความง่าย
    profile = api_data.get('profile', {})
    metrics = api_data.get('metrics', {})
    growth = api_data.get('growth', {})
    cf_latest = api_data.get('cashflow', [{}])[0] if api_data.get('cashflow') else {}
    bs_latest = api_data.get('balance_sheet', {})
    
    # แมปปิ้งตัวแปรให้ตรงกับตรรกะเดิมของคุณ
    shares_outstanding = profile.get('mktCap', 0) / profile.get('price', 1) if profile.get('price') else 0
    earnings_growth = growth.get('netIncomeGrowth', 0) # ใช้ Net Income Growth แทน
    
    # ---- ส่วนที่ 1: DCF จาก Free Cash Flow (หาก Growth >= 10%) ----
    if earnings_growth >= 0.1:
        # FMP มีค่า Free Cash Flow ให้ตรงๆ ไม่ต้องคำนวณเอง
        latest_fcf = cf_latest.get('freeCashFlow', 0)
        
        # หาก FMP ไม่มีค่า ให้ใช้สูตรสำรองแบบเดิมของคุณ
        if not latest_fcf:
            ocf = cf_latest.get('operatingCashFlow', 0)
            capex = abs(cf_latest.get('capitalExpenditure', 0))
            latest_fcf = ocf - capex
            
        growth_rate = earnings_growth # FMP รายไตรมาสแบบละเอียดอาจต้องใช้อีก endpoint ในที่นี้อิงจากรายปีเพื่อความเสถียร
        
        projected_fcf = []
        pv_fcf = []
        discount_rate = 0.09
        terminal_growth = 0.02
        current_fcf = latest_fcf
        
        for year in range(1, 6):
            current_fcf *= (1 + growth_rate)
            projected_fcf.append(current_fcf)
            pv = current_fcf / ((1 + discount_rate)**year)
            pv_fcf.append(pv)
            
        if projected_fcf and shares_outstanding > 0:
            fcf_year_5 = projected_fcf[-1]
            terminal_value = (fcf_year_5 * (1 + terminal_growth)) / (discount_rate - terminal_growth)
            pv_terminal_value = terminal_value / ((1 + discount_rate) ** 5)
            
            g_intrinsic_value = sum(pv_fcf) + pv_terminal_value
            g_value_per_share = g_intrinsic_value / shares_outstanding
            
            score_collect.append({'value': g_value_per_share, 'stock_rated': g_value_per_share})
            
            # คำนวณคะแนนตามสูตรเดิมของคุณ
            earnings_growth_percentage = earnings_growth * 100
            score_growth = (earnings_growth_percentage - 10) / (20 - 10) * 10
            st.write(f"DCF Model - This stock rate out of 10: {score_growth:.2f}")

    # ---- ส่วนที่ 2: Dividend Discount Model (หาก Dividend Yield <= 4%) ----
    # หมายเหตุ: FMP ให้ค่า Dividend Yield เป็นเปอร์เซ็นต์เต็ม (เช่น 1.5 หมายถึง 1.5%)
    dividend_yield_raw = profile.get('lastDiv', 0) / profile.get('price', 1) if profile.get('price') else 0
    
    if dividend_yield_raw <= 0.04 and dividend_yield_raw > 0:
        roe = metrics.get('returnOnEquityTTM', 0)
        payout_ratio = metrics.get('payoutRatioTTM', 0)
        
        g = roe * (1 - payout_ratio)
        d_0 = profile.get('lastDiv', 0)
        d_1 = d_0 * (1 + g)
        r = 0.08
        mos = 0.25
        
        # ป้องกันการหารด้วยศูนย์หาก r น้อยกว่าหรือเท่ากับ g
        if (r - g) > 0:
            d_intrinsic_value = d_1 / (r - g)
            intrinsic_value_price = d_intrinsic_value * (1 - mos)
            rate_dividend = dividend_yield_raw * 100
            
            score_collect.append({'value': intrinsic_value_price, 'stock_rated': rate_dividend})
            score_dividend = (rate_dividend - 4) / (6 - 4) * 10
            st.write(f"Dividend Model - This stock rate out of 10: {score_dividend:.2f}")

    # ---- ส่วนที่ 3: Net Asset Value Model (หาก PBV <= 1.5) ----
    pbv = metrics.get('priceToBookRatioTTM', 999) # ตั้ง default ไว้สูงๆ หากหาค่าไม่ได้
    if pbv <= 1.5 and shares_outstanding > 0:
        total_assets = bs_latest.get('totalAssets', 0)
        total_liabilities = bs_latest.get('totalLiabilities', 0)
        
        nav_per_shares = (total_assets - total_liabilities) / shares_outstanding
        nav_per_shares_price = nav_per_shares * 1.0
        rate_assets = (1 / pbv) * 100
        
        score_collect.append({'value': nav_per_shares_price, 'stock_rated': rate_assets})
        st.write(f"Asset Model - PBV is attractive: {pbv:.2f}")
        
    return score_collect

# --- ส่วนแสดงผลบน Streamlit ---
if premium_user_stock:
    results = calculate_fmp(premium_user_stock)
    final_price = 0
    
    if results:
        def safe_int(val):
            try:
                return int(float(val))
            except (ValueError, TypeError):
                return 0
                
        total_rate = sum(safe_int(item['stock_rated']) for item in results)
        
        for item in results:
            if total_rate > 0:
                weight = safe_int(item['stock_rated']) / total_rate
                final_price += item['value'] * weight
        
        st.subheader("Valuation Results")
        st.write(f"Real value of stock: **{final_price:,.2f} $**")
        
        safe_margin = final_price * 0.2
        buy_margin_price = final_price - safe_margin
        st.write(f"Buy price with 20% margin: **{buy_margin_price:,.2f} $**")
        
        sell_margin_price = final_price + safe_margin
        st.write(f"Sell price with 20% margin: **{sell_margin_price:,.2f} $**")
    else:
        st.warning("No valuation models triggered for this stock based on current criteria.")
  
