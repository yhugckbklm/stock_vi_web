from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from split_dcf import pull_sec_data

app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class stock_title(BaseModel):
  message : str

@app.post("/")
async def receive_stock_title(data: stock_title):
    received_s_t = data.message
    r_s_info = pull_sec_data(received_s_t)
    return {
        "response_stock_info" : r_s_info
    }