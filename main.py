from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from scanners import execute_penny_scan
import json
import os

app = FastAPI()

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scanner Terminal</title>
    <style>
        :root {
            --bg-color: #F0F8FF;
            --surface: #FFFFFF;
            --border: #BAE6FD;
            --primary: #0284C7;
            --primary-hover: #0369A1;
            --text-main: #0F172A;
            --text-muted: #64748B;
            --green: #10B981;
            --red: #EF4444;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }

        .container {
            background-color: var(--surface);
            width: 100%;
            max-width: 1000px;
            padding: 30px;
            border-radius: 16px;
            border: 2px solid var(--border);
            box-shadow: 0 10px 25px rgba(2, 132, 199, 0.1);
        }

        h1 {
            color: var(--primary);
            margin-top: 0;
            border-bottom: 3px dashed var(--border);
            padding-bottom: 15px;
        }

        .controls {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .input-field {
            padding: 12px;
            border: 2px solid var(--border);
            border-radius: 8px;
            font-weight: 600;
            font-size: 16px;
            flex: 1;
            min-width: 200px;
            outline: none;
        }

        .input-field:focus { border-color: var(--primary); }

        .btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            font-size: 16px;
            transition: 0.2s;
            white-space: nowrap;
        }

        .btn:hover { background: var(--primary-hover); transform: translateY(-2px); }
        .btn-scan { background: var(--green); width: 100%; font-size: 18px; margin-top: 10px; }
        .btn-scan:hover { background: #059669; }

        .ticker-wheel {
            display: flex;
            gap: 10px;
            overflow-x: auto;
            padding: 15px;
            background: #F8FAFC;
            border: 2px solid var(--border);
            border-radius: 8px;
            margin-bottom: 20px;
            white-space: nowrap;
        }

        .ticker-pill {
            background: var(--surface);
            border: 2px solid var(--primary);
            color: var(--primary);
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .delete-btn {
            background: none;
            border: none;
            color: var(--red);
            font-weight: bold;
            cursor: pointer;
            padding: 0;
            font-size: 16px;
        }

        .grid-layout {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .pos-card {
            background: var(--surface);
            border: 2px solid var(--border);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(2, 132, 199, 0.05);
            display: flex;
            flex-direction: column;
            transition: transform 0.2s;
        }

        .pos-card:hover { transform: translateY(-4px); border-color: var(--primary); }

        .pos-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px dashed var(--border);
            padding-bottom: 12px;
            margin-bottom: 12px;
        }

        .pos-sym {
            font-size: 24px;
            font-weight: 900;
            color: var(--primary);
            margin: 0;
        }

        .pos-stat {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-weight: bold;
            font-size: 15px;
            align-items: center;
            color: var(--text-muted);
        }

        .pos-stat span:last-child { color: var(--text-main); }
        .text-green { color: var(--green) !important; font-weight: 900; }
        
        .loader {
            display: none;
            text-align: center;
            margin-top: 20px;
            font-weight: bold;
            color: var(--primary);
            font-size: 18px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Penny Scanner Terminal</h1>
        
        <div class="controls">
            <input type="text" id="new-ticker" class="input-field" placeholder="Enter Temporary Ticker (e.g., TSLA)" onkeypress="handleEnter(event)">
            <button class="btn" onclick="addTicker()">Add to Wheel</button>
        </div>

        <div class="ticker-wheel" id="ticker-wheel">
            <span style="color: var(--text-muted); font-weight: bold;">Loading watchlist...</span>
        </div>

        <button class="btn btn-scan" onclick="runScanner()">Execute Scan</button>
        
        <div id="loading" class="loader">Fetching market data and executing scan... please wait.</div>
        <div class="grid-layout" id="scanner-output"></div>
    </div>

    <script>
        let tickers = [];

        // Fetch watchlist.json data from the backend
        async function loadWatchlist() {
            try {
                const res = await fetch('/api/watchlist');
                const data = await res.json();
                tickers = data.map(item => item.Symbol);
                renderWheel();
            } catch (e) {
                console.error("Failed to load watchlist", e);
                document.getElementById('ticker-wheel').innerHTML = '<span style="color: var(--red); font-weight: bold;">Failed to load watchlist.json.</span>';
            }
        }

        function renderWheel() {
            const wheel = document.getElementById('ticker-wheel');
            wheel.innerHTML = '';
            
            if (tickers.length === 0) {
                wheel.innerHTML = '<span style="color: var(--text-muted); font-weight: bold;">No tickers available.</span>';
                return;
            }

            tickers.forEach(sym => {
                wheel.innerHTML += `
                    <div class="ticker-pill">
                        ${sym}
                        <button class="delete-btn" onclick="removeTicker('${sym}')">✕</button>
                    </div>
                `;
            });
        }

        function addTicker() {
            const input = document.getElementById('new-ticker');
            const sym = input.value.trim().toUpperCase();
            
            if (sym && !tickers.includes(sym)) {
                tickers.unshift(sym); // Add new manual tickers to the front
                input.value = '';
                renderWheel();
            }
        }

        function handleEnter(e) {
            if (e.key === 'Enter') addTicker();
        }

        function removeTicker(sym) {
            tickers = tickers.filter(t => t !== sym);
            renderWheel();
        }

        async function runScanner() {
            if (tickers.length === 0) return alert("Add at least one ticker to scan.");
            
            const out = document.getElementById('scanner-output');
            const loader = document.getElementById('loading');
            
            out.innerHTML = '';
            loader.style.display = 'block';
            
            try {
                const tickerQuery = tickers.join(',');
                const res = await fetch(`/scan?tickers=${encodeURIComponent(tickerQuery)}`);
                const data = await res.json();
                
                loader.style.display = 'none';

                if (data.status === 'success' && Array.isArray(data.data) && data.data.length > 0) {
                    data.data.forEach(item => {
                        out.innerHTML += `
                            <div class="pos-card">
                                <div class="pos-header">
                                    <h3 class="pos-sym">${item.symbol}</h3>
                                </div>
                                <div class="pos-stat"><span>Current Price:</span> <span>$${item.current_price.toFixed(2)}</span></div>
                                <div class="pos-stat"><span>Target Exit:</span> <span class="text-green">$${item.target_exit.toFixed(2)}</span></div>
                                <div class="pos-stat"><span>Profit Margin:</span> <span class="text-green">$${item.expected_margin.toFixed(2)}</span></div>
                                <div class="pos-stat"><span>Days to Profit:</span> <span>${item.est_days.toFixed(1)} Days</span></div>
                            </div>
                        `;
                    });
                } else if (data.status === 'success') {
                    out.innerHTML = `<div style="grid-column: 1/-1; font-weight: bold; color: var(--text-muted); text-align: center;">No targeted assets met the required technical thresholds.</div>`;
                } else {
                    out.innerHTML = `<div style="grid-column: 1/-1; color: var(--red); font-weight: bold;">Scan Error.</div>`;
                }
            } catch (e) {
                loader.style.display = 'none';
                out.innerHTML = `<div style="grid-column: 1/-1; color: var(--red); font-weight: bold;">Network failure during scan.</div>`;
            }
        }

        // Initialize UI by fetching the JSON
        loadWatchlist();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return html_content

@app.get("/api/watchlist")
def get_watchlist():
    try:
        with open("watchlist.json", "r") as file:
            return json.load(file)
    except Exception:
        return []

@app.get("/scan")
def run_scan(tickers: str = Query(default="AAPL,MSFT")):
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    return {"status": "success", "data": execute_penny_scan(ticker_list)}
