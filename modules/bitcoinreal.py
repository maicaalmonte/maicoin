import ccxt  # Import ccxt for exchange interactions
import pandas as pd  # Import pandas for data handling
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import time  # Import time for sleep functionality
import os  # For checking and saving CSV files


# Define the function to fetch data with retries
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


# Function to plot real-time data interactively
def plot_realtime_data_interactive(exchange_name, symbol, timeframe):
    # Initialize the exchange object
    exchange = getattr(ccxt, exchange_name)()

    # Initialize the plotly figure
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.1, row_heights=[0.8, 0.2])

    fig.update_layout(title=f'{symbol} Price (Real-time)',
                      xaxis_title='Time',
                      yaxis_title='Price (USDT)',
                      yaxis2_title='Volume',
                      template="plotly_dark")

    # File for data persistence
    file_name = f'{symbol.replace("/", "_")}_data.csv'

    while True:
        # Fetch data
        data = fetch_data_with_retry(exchange, symbol, timeframe, limit=100)
        if data:
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Save data to a CSV file
            if os.path.exists(file_name):
                df.to_csv(file_name, mode='a', header=False, index=False)
            else:
                df.to_csv(file_name, index=False)

            # Update the candlestick chart
            fig.data = []  # Clear previous traces
            fig.add_trace(go.Candlestick(
                x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Candlestick'
            ), row=1, col=1)

            # Add volume as a bar chart
            fig.add_trace(go.Bar(
                x=df['date'],
                y=df['volume'],
                name='Volume',
                marker_color='blue'
            ), row=2, col=1)

            # Update the chart
            fig.show()

        time.sleep(60)  # Wait for 1 minute before fetching data again


# Example usage
plot_realtime_data_interactive('kraken', 'BTC/USDT', '1m')
