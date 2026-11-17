import os
from edgar import Company, set_identity
import pandas as pd
import json

def pull_sec_data(recieved_s_t):
    
    set_identity("dcf nihilis44@gmail.com")
    nvidia = Company(recieved_s_t)
    financials = nvidia.get_financials()
    df_income = financials.income_statement().to_dataframe()
    df_income = df_income.reset_index()
    json_str = df_income.to_json(orient="records")
    return json.loads(json_str)
    

