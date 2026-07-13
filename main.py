from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from scanners import execute_penny_scan

app = FastAPI()

# Embedded HTML, CSS, and JavaScript
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Technical Scanner</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f8ff; /* Light blue background */
            color: #333;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }
        .container {
            background-color: #ffffff;
            width: 100%;
            max-width: 800px;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 90, 156, 0.1);
        }
        h1 {
            color: #005a9c; /* Darker blue header */
            margin-top: 0;
        }
        label {
            font-weight: bold;
            color: #005a9c;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0 20px 0;
            border: 1px solid #b0c4de;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #005a9c;
            color: #ffffff;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background-color: #004170;
        }
        .loader {
            display: none;
            text-align: center;
            margin-top: 20px;
            font-weight: bold;
            color: #005a9c;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #b0c4de;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #e6f2ff; /* Very light blue header */
            color: #005a9c;
        }
        tr:nth-child(even) {
            background-color: #f9fcff;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Technical Scanner</h1>
        <label for="tickers">Enter Tickers (comma-separated):</label>
        <input type="text" id="tickers" value="AAPL,MSFT,NVDA" placeholder="e.g. AAPL,MSFT,TSLA">
        <button onclick="startScan()">Start Scan</button>
        
        <div id="loading" class="loader">Executing scan... please wait.</div>
        <div id="results"></div>
    </div>

    <script>
        async function startScan() {
            const tickers = document.getElementById('tickers').value;
            const resultsDiv = document.getElementById('results');
            const loadingDiv = document.getElementById('loading');
            
            // Clear previous results and show loader
            resultsDiv.innerHTML = '';
            loadingDiv.style.display = 'block';
            
            try {
                // Call the existing API endpoint
                const response = await fetch(`/scan?tickers=${encodeURIComponent(tickers)}`);
                const data = await response.json();
                
                if (data.status === 'success' && data.data.length > 0) {
                    let table = '<table><tr><th>Symbol</th><th>Current Price</th><th>Target Exit (SMA)</th><th>Expected Margin</th><th>Est Reversion Days</th></tr>';
                    
                    data.data.forEach(item => {
                        table += `<tr>
                            <td><strong>${item.symbol}</strong></td>
                            <td>$${item.current_price.toFixed(2)}</td>
                            <td>$${item.target_exit.toFixed(2)}</td>
                            <td>$${item.expected_margin.toFixed(2)}</td>
                            <td>${item.est_days.toFixed(1)}</td>
                        </tr>`;
                    });
                    
                    table += '</table>';
                    resultsDiv.innerHTML = table;
                } else if (data.status === 'success') {
                    resultsDiv.innerHTML = '<p style="color: #666; margin-top: 20px;">No stocks met the scanner criteria.</p>';
                } else {
                    resultsDiv.innerHTML = '<p style="color: red; margin-top: 20px;">Error executing scan.</p>';
                }
            } catch (error) {
                resultsDiv.innerHTML = `<p style="color: red; margin-top: 20px;">Network error: ${error.message}</p>`;
            } finally {
                // Hide loader
                loadingDiv.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return html_content

@app.get("/scan")
def run_scan(tickers: str = Query(default="AAPL,MSFT")):
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    return {"status": "success", "data": execute_penny_scan(ticker_list)}
