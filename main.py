from fastapi import FastAPI, Query
from scanners import execute_penny_scan

app = FastAPI()

@app.get("/api/scan")
def run_scan(tickers: str = Query(default="AAPL,MSFT,NVDA", description="Comma-separated ticker symbols")):
    # Clean and split the URL parameter into a Python list
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    
    # Execute scanner
    results = execute_penny_scan(ticker_list)
    
    return {"status": "success", "data": results}