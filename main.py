from fastapi import FastAPI, Query
from scanners import execute_penny_scan

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "alive", "message": "API built successfully."}

@app.get("/scan")
def run_scan(tickers: str = Query(default="AAPL,MSFT")):
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    return {"status": "success", "data": execute_penny_scan(ticker_list)}
