import os
from edgar import Company, set_identity
import pandas as pd

def pull_sec_data(recieved_s_t):
    
    set_identity("dcf nihilis44@gmail.com")
    nvidia = Company(received_s_t)
    financials = nvidia.get_financials()
    df_income = financials.income_statement().to_dataframe()
    return df_income
    

