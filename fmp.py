import requests
api_key = 'UufVcJGBxAtLUtSOonJAZt2KsstmrVFe'
ticker = 'APPL'
base_url = 'https://financialmodelingprep.com/api/v3'

    # 1. ดึงงบกระแสเงินสดล่าสุด
cf_url = f'{base_url}/cash-flow-statement/{ticker}?limit=1&apikey={api_key}'
cf_res = requests.get(cf_url).json()
print(cf_res)