import matplotlib.pyplot as plt  # Import plt here
import matplotlib.animation as animation
import pandas as pd
import ccxt  # Import ccxt for exchange objects
import time

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

# Function to update the plot
def update_plot(i, df, ax, exchange, symbol, timeframe):
    data = fetch_data_with_retry(exchange, symbol, timeframe, limit=100)
    if data:
        new_df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        new_df['date'] = pd.to_datetime(new_df['timestamp'], unit='ms')

        # Update the plot
        df = new_df
        ax.clear()
        ax.plot(df['date'], df['close'])
        ax.set_title('Ethereum Price (Real-time updates)')
        ax.set_xlabel('Date')
        ax.set_ylabel('Close Price (USDT)')
        ax.tick_params(axis='x', rotation=45)

# Plot real-time data
def plot_realtime_data(exchange_name, symbol, timeframe):
    # Initialize the exchange object using ccxt
    exchange = getattr(ccxt, exchange_name)()  # Dynamically load the exchange class
    fig, ax = plt.subplots()
    ani = animation.FuncAnimation(fig, update_plot, fargs=(pd.DataFrame(), ax, exchange, symbol, timeframe),
                                  interval=60000)  # Update every 60 seconds (1 minute)
    plt.show()

# Example usage for Ethereum (ETH/USD)
plot_realtime_data('kraken', 'ETH/USD', '1m')  # Ethereum price on Kraken with 1-minute intervals
