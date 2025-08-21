from flask import Flask, render_template_string
import yfinance as yf
import pandas as pd
import io, base64
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route("/")
def index():
    symbol = "AAPL"

    try:
        # Try downloading stock data
        df = yf.download(symbol, period="1mo", interval="1d")
        if df.empty:
            raise ValueError("No data returned")

        last_price = df["Close"].iloc[-1]
        signal = "BUY" if df["Close"].iloc[-1] > df["Close"].rolling(5).mean().iloc[-1] else "SELL"

        # Plot chart
        fig, ax = plt.subplots()
        df["Close"].plot(ax=ax, title=f"{symbol} Price")
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)

    except Exception as e:
        last_price = "N/A"
        signal = "N/A"
        img_b64 = ""
        error_msg = f"⚠️ Data fetch/plot failed: {e}"
    else:
        error_msg = ""

    html = f'''
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
    <body style="font-family:sans-serif; text-align:center;">
        <h1>{symbol} Dashboard</h1>
        <p><b>Last Price:</b> {last_price}</p>
        <p><b>Signal:</b> {signal}</p>
        {'<img src="data:image/png;base64,' + img_b64 + '" style="max-width:100%;"/>' if img_b64 else ''}
        <p style="color:red;">{error_msg}</p>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
