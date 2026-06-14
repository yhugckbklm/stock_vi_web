import streamlit as st
import yfinance as yf
import pandas as pd
import edgar
edgar.set_identity("nihilis44@gmail.com")


st.header("Welcome to Premium")

col1 = st.columns(1)[0] 

with col1:
    ticker_symbol = st.session_state.selected_item
    st.write(ticker_symbol)
def calculate(ticker_symbol):
    score_collect = []
    
    if not ticker_symbol:
        return score_collect
        
    try:
        # 1. ดึงข้อมูลจาก edgartools
        company = edgar.Company(ticker_symbol)
        filings = company.get_filings(form="10-K")
        latest_filing = filings.latest()
        financials = latest_filing.xbrl()
        statements = financials.statements
        # แปลงงบต่าง ๆ เป็น DataFrame
        df_income = statements.income_statement().to_dataframe()
        df_balance = statements.balance_sheet().to_dataframe()
        
        # ดึงจำนวนหุ้นจากระบบ EDGAR
        shares_outstanding = company.shares_outstanding
        if not shares_outstanding:
            shares_outstanding = 1  # กันหารด้วยศูนย์
            
    except Exception as e:
        st.error(f"ไม่สามารถดึงข้อมูล SEC สำหรับหุ้น {ticker_symbol} ได้: {e}")
        return score_collect

    # ----------------------------------------------------
    # ส่วนที่ 1: หุ้นประเภท Growth (คิดจาก Net Income เติบโต)
    # ----------------------------------------------------
    try:
        # ค้นหาแถว Net Income
        net_income_row = df_income[df_income.index.str.contains('Net Income', case=False)]
        net_income_this_year = float(net_income_row.iloc[0, 0])
        net_income_last_year = float(net_income_row.iloc[0, 1])
        
        # คำนวณ Earnings Growth
        earnings_growth = (net_income_this_year - net_income_last_year) / abs(net_income_last_year)
        
       
        if earnings_growth >= 0.15:
            # คำนวณ EPS ปีนี้
            eps_this_year = net_income_this_year / shares_outstanding
            
            # คำนวณราคาประเมินจาก PEG และคะแนนเติบโต
            peg_ratio_price = eps_this_year * (earnings_growth * 100)
            rate_growth = (earnings_growth / 0.20) * 100
            
            score_collect.append({
                'is_stock': 'is_growth',
                'value': peg_ratio_price,
                'stock_rated': rate_growth,
                'growth_val': earnings_growth
            })

            
    except Exception:
        pass  # ข้ามหากคำนวณหมวดเติบโตไม่ได้

    # ----------------------------------------------------
    # ส่วนที่ 2: หุ้นประเภท Dividend (คำนวณหามูลค่าที่แท้จริงจากปันผล)
    # ----------------------------------------------------
    try:
        # ระบบ EDGAR ดิบไม่มีข้อมูลปันผลตรง ๆ จึงขอสมมติจำลองสัดส่วนตามเงื่อนไขเดิมของคุณ
        # (หมายเหตุ: ปันผลปกติแนะนำดึงผ่านตลาดทุนเพิ่ม แต่โครงสร้างนี้เขียนให้รันตามตรรกะเดิมของคุณได้)
        dividend_yield = 0.05   # สมมติ 5% เพื่อให้เข้าเงื่อนไขตัวอย่างของคุณ
        payout_ratio = 0.40     # สมมติ 40%
        dividend_rate = 2.5     # สมมติเงินปันผล 2.5 ดอลลาร์
        
        if dividend_yield > 0.04:
            # ดึงข้อมูลส่วนผู้ถือหุ้นมาคำนวณ ROE
            equity_row = df_balance[df_balance.index.str.contains("Stockholders' Equity", case=False)]
            total_equity = float(equity_row.iloc[0, 0])
            
            roe = net_income_this_year / total_equity
            g = roe * (1 - payout_ratio)
            d_1 = dividend_rate * (1 + g)
            
            r = 0.08  # ปรับเป็น 0.08 (8%) เพราะหากใช้ 0.8 (80%) มูลค่าจะเพี้ยนมากครับ
            mos = 0.25 # ปรับเป็น 0.25 (25%) ตามหลัก Margin of Safety
            
            # กันส่วนหารติดลบหรือเป็นศูนย์
            if (r - g) > 0:
                intrinsic_value = d_1 / (r - g)
                intrinsic_value_price = intrinsic_value * (1 - mos)
                rate_dividend = (dividend_yield / 0.04) * 100
                
                score_collect.append({
                    'is_stock': 'is_dividend',
                    'value': intrinsic_value_price,
                    'stock_rated': rate_dividend,
                    'dividend_val': dividend_yield
                })
    except Exception:
        pass

    # ----------------------------------------------------
    # ส่วนที่ 3: หุ้นประเภท Assets (คำนวณจากทรัพย์สิน NAV)
    # ----------------------------------------------------
    try:
        # ค้นหา Total Assets และ Total Liabilities จากงบดุล
        assets_row = df_balance[df_balance.index.str.contains('Total Assets', case=False)]
        liabilities_row = df_balance[df_balance.index.str.contains('Total Liabilities', case=False)]
        
        total_assets = float(assets_row.iloc[0, 0])
        total_liabilities = float(liabilities_row.iloc[0, 0])
        
        # คำนวณหา Book Value และจำลองค่า P/BV
        book_value = total_assets - total_liabilities
         # สมมติราคาปิดเข้าเงื่อนไข P/BV < 1.5
        bvps = book_value / shares_outstanding
        ticker = yf.Ticker(ticker_symbol)
        current_price = ticker.info.get('currentPrice')
        pbv = current_price / bvps
        if pbv < 1.5:
            nav_per_share = book_value / shares_outstanding
            nav_per_shares_price = nav_per_share * 1.0
            rate_assets = (1 / pbv) * 100
            
            score_collect.append({
                'is_stock': 'is_assets',
                'value': nav_per_shares_price,
                'stock_rated': rate_assets  # ใช้ชื่อคีย์ให้เหมือนกันเพื่อนำไปวนลูปด้านล่างได้
            })
    except Exception:
        pass

    return score_collect

# --- ส่วนประมวลผลและแสดงผลบน Streamlit ---
if ticker_symbol:
    results = calculate(ticker_symbol)
    
    if not results:
        st.error("No assessment criteria met or results not found for this stock.")
    else:
        # คำนวณหาน้ำหนักรวมถ่วงน้ำหนัก (Weighted Average Price)
        total_rate = sum(item['stock_rated'] for item in results)
        final_price = 0.0
        
        if total_rate > 0:
            for item in results:
                weight = item['stock_rated'] / total_rate
                final_price += item['value'] * weight 
        
        # แสดงราคามูลค่าที่แท้จริง
        st.subheader("📊 Stock Valuation Analysis")
        st.write(f"**Real value of stock:** ${final_price:,.2f}")
        
        # คำนวณกรอบการซื้อและขายตาม Margin 20%
        margin_price = final_price * 0.20
        buy_margin_price = final_price - margin_price
        sell_margin_price = final_price + margin_price
        
        st.success(f"🟩 **Buy price with 20% margin:** ${buy_margin_price:,.2f}")
        st.danger(f"🟥 **Sell price with 20% margin:** ${sell_margin_price:,.2f}")
        
        # แสดงคะแนนแยกตามหมวดหมู่ (ดึงค่าจากผลลัพธ์มาคำนวณสเกลคะแนน)
        st.markdown("---")
        st.subheader("🎯 Stock Scores (Out of 10)")
        
        growth_item = next((i for i in results if i['is_stock'] == 'is_growth'), None)
        if growth_item:
            score_growth = ((growth_item['growth_val'] * 100) - 10) / (20 - 10) * 10
            # จำกัดคะแนนให้อยู่ในช่วง 0-10
            score_growth = max(0.0, min(10.0, score_growth))
            st.write(f"📈 **Growth Score:** {score_growth:.2f} / 10")
        else:
            st.write("📈 **Growth Score:** N/A (เงื่อนไขไม่ตรง)")
            
        div_item = next((i for i in results if i['is_stock'] == 'is_dividend'), None)
        if div_item:
            score_dividend = ((div_item['dividend_val'] * 100) - 4) / (6 - 4) * 10
            score_dividend = max(0.0, min(10.0, score_dividend))
            st.write(f"💰 **Dividend Score:** {score_dividend:.2f} / 10")
        else:
            st.write("💰 **Dividend Score:** N/A (เงื่อนไขไม่ตรง)")
