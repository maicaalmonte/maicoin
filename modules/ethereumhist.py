import ccxt
import matplotlib.pyplot as plt
import pandas as pd
import time
import requests

# Function to fetch data with retries
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

# Function to check API status with retries
def check_api_status_with_retry(api_url):
    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(api_url)
            print(f"API Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error checking API status on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print("Max retries reached for checking API status.")
                return None

# Function to plot data
def plot_data(df):
    plt.plot(df['date'], df['close'])
    plt.title('Ethereum Price (Last 100 Days)')
    plt.xlabel('Date')
    plt.ylabel('Close Price (USDT)')
    plt.xticks(rotation=45)
    plt.show()

# Main function to get and plot data
def main(exchange_name, symbol, timeframe):
    exchange = getattr(ccxt, exchange_name)()  # Dynamically load the exchange
    print(f"Using exchange: {exchange_name}")

    # Fetch data
    data = fetch_data_with_retry(exchange, symbol, timeframe)

    if data:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')

        plot_data(df)
    else:
        exchange_url = f"https://api.{exchange_name.lower()}.com/api/v3/exchangeInfo"
        check_api_status_with_retry(exchange_url)

# Example usage: Use Kraken, Coinbase, or any other supported exchange
main('kraken', 'ETH/USD', '1d')  # Ethereum price on Kraken with 1-day intervals
