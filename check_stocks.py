import yfinance as yf
import streamlit as st
import pandas as pd
import edgar

edgar.set_identity("nihilis44@gmail.com")
premium_user_stock = st.session_state.selected_item
st.write(premium_user_stock)
def calculate(premium_user_stock):
  company = edgar.Company(premium_user_stock)
  fillings = company.get_filings(form="10-K")
  latest_filling = fillings.lastest
  financials = latest_filling.financial()
  st.write(financials)
  income_statement = financials.get_income_statement()
  balance_sheet = financials.get_balance_sheet()
  cash_flow1 = financials.get_cash_flow_statement()
  
  df_income = income_statement.to_dataframe()
  df_balance = balance_sheet.to_dataframe()
  df_cf = cash_flow1.to_dataframe()
  
  shares_outstanding = latest_filling.shares_outstanding
  
  {
    "income" : df_income,
    "balance" : df_balance,
    "cash_flow" : df_cf,
    "shares" : shares_outstanding,
  }
  
  score_collect = []
  ticker = yf.Ticker(premium_user_stock)
  info = ticker.info
  net_income_this_year = df_income.loc["Net income"].iloc[0]
  net_income_last_year = df_income.loc["Net income"].iloc[1]
  calculated_growth = (net_income_this_year - net_income_last_year) / abs(net_income_last_year)

  if calculated_growth >= 0.1:
    try:
      cash_flow = ticker.cashflow
      latest_fcf = cash_flow.loc['Free Cash Flow'].iloc[0]
    except:
      ocf = cash_flow.loc['Cash Flow From Continuing Operating Activities'].iloc[0]
      capex = abs(cash_flow.loc['Capital Expenditures'].iloc[0])
      latest_fcf = ocf - capex
      
    growth_rate = info.get('earningsQuarterlyGrowth')
    projected_fcf = []
    pv_fcf = []
    discount_rate = 0.09
    terminal_growth = 0.02
    current_fcf = latest_fcf
    for year in range(1,6):
      
      current_fcf*=(1 + growth_rate)
      projected_fcf.append(current_fcf)
        
      pv = current_fcf / ((1 + discount_rate)**year)
      pv_fcf.append(pv)
    
    fcf_year_5 = projected_fcf[-1]
    terminal_value = (fcf_year_5*(1+terminal_growth)) / (discount_rate - terminal_growth)
    pv_terminal_value = terminal_value / ((1 + discount_rate) ** 5)
    
    g_intrinsic_value = sum(pv_fcf) + pv_terminal_value
    shares_outstanding = info.get('sharesOutstanding')
    
    g_value_per_share = g_intrinsic_value / shares_outstanding
    score_collect.append({'value':g_value_per_share,'stock_rated':g_value_per_share})
    earnings_growth = info.get('earningsGrowth')
    earnings_growth_percentage = earnings_growth * 100
    score_growth = (earnings_growth_percentage - 10) / ( 20 - 10 ) * 10
    st.write("This stock rate out of 10:", score_growth)
     
  dividend_yield = info.get('dividendYield')
  payout_ratio = info.get('payoutRatio')
  if dividend_yield <= 0.04:
    roe = info.get('returnOnEquity')
    payout_ratio = info.get('payoutRatio')
    g = roe * (1 - payout_ratio)
    d_0 = info.get('dividendRate')
    d_1 = d_0 * (1 + g)
    r = 0.08
    mos = 0.25
    d_intrinsic_value = d_1 / (r- g)
    intrinsic_value_price = d_intrinsic_value * (1 - mos)
    rate_dividend = ( dividend_yield ) * 100
    score_collect.append({'value':intrinsic_value_price,'stock_rated':rate_dividend})
    dividend_yield = info.get('dividendYield')
    score_dividend = ( dividend_yield - 4 ) / ( 6 - 4 ) * 10
    st.write("This stock rate out of 10:", score_dividend)
  
  pbv = info.get('priceToBook')
  if pbv <= 1.5:
    total_assets = ticker.quarterly_balance_sheet('Total Assets')
    total_liabilities = ticker.quarterly_balance_sheet('Total Liabilities Net Minority Interest')
    shares_outstanding = info.get('sharesOutstanding')
    nav_per_shares = (total_assets - total_liabilities) / shares_outstanding
    nav_per_shares_price = nav_per_shares * 1.0
    rate_assets = ( 1 / pbv ) * 100
    score_collect.append({'value':nav_per_shares_price,'stock_rated':rate_assets})
  if not score_collect:
    return 0
  return score_collect

results = calculate(premium_user_stock)
final_price = 0
if results:
  def safe_int(val):
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0
  total_rate = sum(safe_int(item['stock_rated']) for item in results)
  
  for item in results:
    if total_rate > 0:
       weight = int(item['stock_rated']) / total_rate
       final_price += item['value'] * weight
    else:
       weight = 0 

real_value = st.write("real value of stock: ",final_price,"$")
safe_margin = final_price * 0.2
buy_margin_price = final_price - safe_margin
buy_price = st.write("buy price with 20% margin:",buy_margin_price,"$")
sell_margin_price = final_price + safe_margin
sell_price = st.write("sell price with 20% margin:",sell_margin_price,"$")
  
