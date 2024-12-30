import ccxt
import pandas as pd
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template_string
import time
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots

app = Flask(__name__)


# Function to fetch data with retries for exchanges
def fetch_data_with_retry(exchange, symbol, timeframe, limit=100):
    retries = 5
    for attempt in range(retries):
        try:
            data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            return data
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print("Max retries reached for fetching data.")
                return None


# Function to fetch data from CoinGecko with retries and rate limit handling
def fetch_data_with_retry_coingecko(url, params, retries=5):
    for attempt in range(retries):
        try:
            print(f"Fetching data... Attempt {attempt + 1}/{retries}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            print("Data fetched successfully!")
            return data
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                wait_time = 2 ** attempt
                print(f"Attempt {attempt + 1} failed: {e}")
                print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    print("Max retries reached. Could not fetch data.")
                    return None
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print("Max retries reached. Could not fetch data.")
                return None


# Function to analyze the best trading opportunities
def analyze_trading_opportunities(data):
    if "prices" not in data:
        print("No price data available for analysis.")
        return None

    prices = data["prices"]  # List of [timestamp, price] pairs
    if not prices:
        print("Price data is empty.")
        return None

    min_price = float('inf')
    max_profit = 0
    buy_time = None
    sell_time = None
    best_buy_price = None
    best_sell_price = None

    for timestamp, price in prices:
        if price < min_price:
            min_price = price
            buy_time = timestamp
            best_buy_price = price

        profit = price - min_price
        if profit > max_profit:
            max_profit = profit
            sell_time = timestamp
            best_sell_price = price

    if max_profit > 0:
        return {
            "best_buy_time": datetime.utcfromtimestamp(buy_time / 1000),
            "best_buy_price": best_buy_price,
            "best_sell_time": datetime.utcfromtimestamp(sell_time / 1000),
            "best_sell_price": best_sell_price,
            "max_profit": max_profit
        }
    else:
        return None


# Function to fetch 100-day historical data from CryptoCompare
def fetch_100_day_historical_data(symbol, currency='USD'):
    url = "https://min-api.cryptocompare.com/data/v2/histoday"
    params = {
        'fsym': symbol,
        'tsym': currency,
        'limit': 100  # Last 100 days
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data.get('Response') == 'Success':
        return data['Data']['Data']
    else:
        print(f"Failed to fetch 100-day historical data for {symbol}")
        return []


# Function to generate Plotly graph for historical data
def plot_historical_data(prices, title):
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    fig = px.line(df, x='date', y='price', title=title)
    return fig.to_html(full_html=False)


# Function to generate Plotly graph for 100-day historical data
def plot_100_day_historical_data(data, title):
    df = pd.DataFrame(data)
    if 'time' in df:
        df['time'] = pd.to_datetime(df['time'], unit='s')
        fig = px.line(df, x='time', y='close', title=title)
        return fig.to_html(full_html=False)
    return "<p>100-Day historical data not available.</p>"


# Function to generate Plotly graph for real-time data
def plot_realtime_data(exchange_name, symbol, timeframe):
    exchange = getattr(ccxt, exchange_name)()
    print(f"Fetching real-time data for {symbol} from {exchange_name} with timeframe {timeframe}")
    data = fetch_data_with_retry(exchange, symbol, timeframe, limit=100)
    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        print(df.head())  # Debug output to verify data
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.8, 0.2])
        fig.add_trace(go.Candlestick(x=df['date'], open=df['open'], high=df['high'], low=df['low'], close=df['close'],
                                     name='Candlestick'), row=1, col=1)
        fig.add_trace(go.Bar(x=df['date'], y=df['volume'], name='Volume', marker_color='blue'), row=2, col=1)
        fig.update_layout(title=f'{symbol} Price (Real-time)', xaxis_title='Time', yaxis_title='Price (USDT)',
                          yaxis2_title='Volume', template="plotly_dark")
        return fig.to_html(full_html=False)
    return "<p>No real-time data available.</p>"


# Define the time range (e.g., last 48 hours)
end_time = int(datetime.now().timestamp())
start_time = end_time - 48 * 3600  # Last 48 hours

# URLs and parameters for different cryptocurrencies
urls_params = [
    {
        "url": "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range",
        "params": {'vs_currency': 'usd', 'from': start_time, 'to': end_time},
        "currency_name": "Bitcoin"
    },
    {
        "url": "https://api.coingecko.com/api/v3/coins/dogecoin/market_chart/range",
        "params": {'vs_currency': 'usd', 'from': start_time, 'to': end_time},
        "currency_name": "Dogecoin"
    },
    {
        "url": "https://api.coingecko.com/api/v3/coins/ethereum/market_chart/range",
        "params": {'vs_currency': 'usd', 'from': start_time, 'to': end_time},
        "currency_name": "Ethereum"
    }
]


@app.route('/')
def index():
    results = []
    for url_params in urls_params:
        url = url_params["url"]
        params = url_params["params"]
        currency_name = url_params["currency_name"]

        data = fetch_data_with_retry_coingecko(url, params)
        if data:
            best_trading_analysis = analyze_trading_opportunities(data)
            historical_graph = plot_historical_data(data['prices'], f'{currency_name} Historical Data')
            realtime_graph = plot_realtime_data('kraken', f'{currency_name}/USD', '1m')

            # Fetch and plot 100-day historical data
            symbol = 'BTC' if currency_name.lower() == 'bitcoin' else currency_name.upper()
            historical_100_day_data = fetch_100_day_historical_data(symbol)
            historical_100_day_graph = plot_100_day_historical_data(historical_100_day_data,
                                                                    f'{currency_name} 100-Day Historical Data')

            results.append({
                "currency_name": currency_name,
                "best_trading_analysis": best_trading_analysis,
                "historical_graph": historical_graph,
                "realtime_graph": realtime_graph,
                "historical_100_day_graph": historical_100_day_graph
            })

    html_content = """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>Cryptocurrency Data</title>
        <style>
          body {
            background-color: black;
            color: white;
            font-family: Arial, sans-serif;
          }
          .container {
            width: 90%;
            margin: 0 auto;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
          }
          th, td {
            border: 1px solid white;
            padding: 10px;
            text-align: center;
          }
          th {
            background-color: #333;
            color: white;
          }
          td {
            background-color: #222;
          }
          .graph {
            width: 100%;
            margin: 20px 0;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>Cryptocurrency Data</h1>
          <p> This is just for fun hihi😂. Just trying to learn web development lol!<p>
          <p> However, the data were sourced through the APIs of respective crypto exchanges, ensuring they are factual.🤗<p>
          <table>
            <tr>
              <th>Currency</th>
              <th>Best Trading Analysis</th>
            </tr>
            {% for result in results %}
            <tr>
              <td>{{ result.currency_name }}</td>
              <td>
                {% if result.best_trading_analysis %}
                  <p>Best Buy Time: {{ result.best_trading_analysis.best_buy_time }} at ${{ result.best_trading_analysis.best_buy_price }}</p>
                  <p>Best Sell Time: {{ result.best_trading_analysis.best_sell_time }} at ${{ result.best_trading_analysis.best_sell_price }}</p>
                  <p>Maximum Profit: ${{ result.best_trading_analysis.max_profit }}</p>
                {% else %}
                  <p>No profitable trading opportunities found.</p>
                {% endif %}
              </td>
            </tr>
            {% endfor %}
          </table>
          {% for result in results %}
            <div class="graph">
              <h2>{{ result.currency_name }} Real-time Price</h2>
              {{ result.realtime_graph | safe }}
            </div>
            <div class="graph">
              <h2>{{ result.currency_name }} Historical Data</h2>
              {{ result.historical_graph | safe }}
            </div>
            <div class="graph">
              <h2>{{ result.currency_name }} 100-Day Historical Data</h2>
              {{ result.historical_100_day_graph | safe }}
            </div>
          {% endfor %}
        </div>
      </body>
    </html>
    """
    return render_template_string(html_content, results=results)


if __name__ == "__main__":
    app.run(port=5000)