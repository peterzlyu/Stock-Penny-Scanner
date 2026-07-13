from fastapi import FastAPI, Query
from scanners import execute_penny_scan

app = FastAPI()

# Root check to verify the app is alive instead of throwing a 404
@app.get("/")
def health_check():
    return {"status": "alive", "message": "API is running. Navigate to /api to scan."}

# The main scanner endpoint matched to Vercel's folder structure
@app.get("/api")
def run_scan(tickers: str = Query(default="AAPL,MSFT,NVDA", description="Comma-separated ticker symbols")):
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    results = execute_penny_scan(ticker_list)
    return {"status": "success", "data": results}
