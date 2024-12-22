from flask import Flask, render_template, url_for
import logging
import os
import socket
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from urllib3.connection import port_by_scheme

from modules.cryptocurrency import get_price
from modules.api import get_prices
from modules.bitcoinreal import plot_realtime_data_interactive as plot_bitcoin_realtime
from modules.ethereumreal import plot_realtime_data as plot_ethereum_realtime
from modules.dogecoinreal import update_plot as plot_dogecoin_realtime
from modules.bitcoinhist import main as plot_bitcoin_hist
from modules.ethereumhist import main as plot_ethereum_hist
from modules.dogecoinhist import fetch_cryptocompare_data as fetch_dogecoin_hist_data
from modules.crypto_analysis import analyze_multiple_cryptos

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Flask app
app = Flask(__name__, static_folder='static')

# Ensure the 'static/img' directory exists for plot saving
plot_dir = os.path.join(app.static_folder, 'img')
os.makedirs(plot_dir, exist_ok=True)

# Function to check if a port is available
def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except socket.error:
            return False

# Function to fetch data from CoinGecko with error handling
def fetch_data_from_coingecko(crypto_id, vs_currency='usd', days='1'):
    url = f'https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart'
    params = {
        'vs_currency': vs_currency,
        'days': days,
        'interval': 'hourly'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from CoinGecko for {crypto_id}: {e}")
        return None

# Real-time data fetch and plot functions for each cryptocurrency
def fetch_and_plot_data(crypto_id, filename, vs_currency='usd', days='1'):
    logging.info(f"Fetching data for {crypto_id}")
    data = fetch_data_from_coingecko(crypto_id, vs_currency, days)

    if data:
        logging.info(f"Fetched data for {crypto_id}, now plotting...")
        try:
            prices = data['prices']
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(df['date'], df['price'], label=f"{crypto_id.capitalize()} Price ({vs_currency.upper()})", color='blue')
            if len(df) > 5:
                sma = df['price'].rolling(window=5).mean()
                ax.plot(df['date'], sma, label="5-Point Moving Average", color='orange', linestyle='--')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator())
            plt.xticks(rotation=45)
            ax.set_title(f"{crypto_id.capitalize()} Price Over Time", fontsize=16)
            ax.set_xlabel("Date", fontsize=12)
            ax.set_ylabel(f"Price ({vs_currency.upper()})", fontsize=12)
            ax.legend()
            ax.grid(True)
            plot_path = os.path.join(plot_dir, filename)
            plt.savefig(plot_path)
            plt.close()
            logging.info(f"Saved plot to {plot_path}")
        except Exception as e:
            logging.error(f"Error while plotting data for {crypto_id}: {e}")
    else:
        logging.error(f"Failed to fetch data for {crypto_id}")

# Fetch real-time data for all cryptocurrencies
def fetch_real_time_data():
    logging.info("Fetching real-time data for all cryptocurrencies")
    fetch_and_plot_data('bitcoin', 'bitcoin_plot.png', 'usd', '1')
    fetch_and_plot_data('dogecoin', 'dogecoin_plot.png', 'usd', '1')
    fetch_and_plot_data('ethereum', 'ethereum_plot.png', 'usd', '1')

# Set up scheduler for background tasks
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_real_time_data, 'interval', minutes=10)  # Adjust interval as needed
scheduler.start()

# Routes for Flask app
@app.route('/')
def home():
    logging.info('Home route accessed')
    return render_template('index.html')

@app.route('/bitcoin')
def bitcoin():
    logging.info('Bitcoin route accessed')
    plot_url = url_for('static', filename='img/bitcoin_plot.png')
    btc_price = get_price('bitcoin', 'usd')
    return render_template('bitcoin.html', plot_url=plot_url, price=btc_price)

@app.route('/dogecoin')
def dogecoin():
    logging.info('Dogecoin route accessed')
    plot_url = url_for('static', filename='img/dogecoin_plot.png')
    doge_price = get_price('dogecoin', 'usd')
    return render_template('dogecoin.html', plot_url=plot_url, price=doge_price)

@app.route('/ethereum')
def ethereum():
    logging.info('Ethereum route accessed')
    plot_url = url_for('static', filename='img/ethereum_plot.png')
    eth_price = get_price('ethereum', 'usd')
    return render_template('ethereum.html', plot_url=plot_url, price=eth_price)

@app.route('/bitcoin/bitcoin-realtime')
def bitcoin_realtime():
    logging.info('Bitcoin Realtime route accessed')
    plot_bitcoin_realtime('kraken', 'BTC/USDT', '1m')
    return render_template('bitcoin_realtime.html')

@app.route('/ethereum/ethereum-realtime')
def ethereum_realtime():
    logging.info('Ethereum Realtime route accessed')
    plot_ethereum_realtime('kraken', 'ETH/USD', '1m')
    return render_template('ethereum_realtime.html')

@app.route('/dogecoin/dogecoin-realtime')
def dogecoin_realtime():
    logging.info('Dogecoin Realtime route accessed')
    plot_dogecoin_realtime()
    return render_template('dogecoin_realtime.html')

@app.route('/bitcoin/bitcoin-historical')
def bitcoin_historical():
    logging.info('Bitcoin Historical route accessed')
    plot_bitcoin_hist('kraken', 'BTC/USD', '1d')
    return render_template('bitcoin_historical.html')

@app.route('/ethereum/ethereum-historical')
def ethereum_historical():
    logging.info('Ethereum Historical route accessed')
    plot_ethereum_hist('kraken', 'ETH/USD', '1d')
    return render_template('ethereum_historical.html')

@app.route('/dogecoin/dogecoin-historical')
def dogecoin_historical():
    logging.info('Dogecoin Historical route accessed')
    data = fetch_dogecoin_hist_data()
    if data is not None:
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(data['time'], data['close'], label="Dogecoin Price (USD)", color='blue')
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
            plt.xticks(rotation=45)
            plt.title("Dogecoin Historical Data (CryptoCompare)", fontsize=16)
            plt.xlabel("Date", fontsize=12)
            plt.ylabel("Price (USD)", fontsize=12)
            plt.legend()
            plt.grid(True)
            plt.show()
        except Exception as e:
            logging.error(f"Error plotting Dogecoin historical data: {e}")
    return render_template('dogecoin_historical.html')

@app.route('/crypto-analysis')
def crypto_analysis():
    logging.info('Crypto Analysis route accessed')
    crypto_ids = ["bitcoin", "ethereum", "dogecoin"]
    analysis_results = analyze_multiple_cryptos(crypto_ids, currency='usd', hours=48)
    return render_template('crypto_analysis.html', analysis_results=analysis_results)

@app.route('/prices')
def display_prices():
    logging.info("Prices route accessed")
    crypto_ids = ['bitcoin', 'ethereum', 'dogecoin']
    current_prices = get_prices(crypto_ids, 'usd')
    return render_template('prices.html', prices=current_prices)

@app.route('/crypto-price/<crypto_id>/<currency>')
def crypto_price(crypto_id, currency):
    logging.info(f"Crypto Price route accessed for {crypto_id} in {currency}")
    try:
        price = get_price(crypto_id, currency)
        return render_template('cryptocurrency.html', crypto_id=crypto_id, currency=currency, price=price)
    except Exception as e:
        logging.error(f"Error fetching price for {crypto_id}: {e}")
        return "Error fetching price."

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 8080))
    if not is_port_available(port):
        logging.error(f"Port {port} is already in use. Please specify a different port.")
    else:
        app.run(debug=False, port=port)
