from fastapi import FastAPI, Query
from scanners import execute_penny_scan

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "alive", "message": "API is running. Navigate to /scan to execute."}

@app.get("/scan")
def run_scan(tickers: str = Query(default="AAPL,MSFT,NVDA")):
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    results = execute_penny_scan(ticker_list)
    return {"status": "success", "data": results}
