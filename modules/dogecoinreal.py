import requests
from time import sleep
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
import numpy as np

# Function to fetch real-time Dogecoin price
def fetch_real_time_data():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {'ids': 'dogecoin', 'vs_currencies': 'usd'}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['dogecoin']['usd'], datetime.now()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch real-time data: {e}")
        return None, None

# Initialize data storage
prices = []
timestamps = []

# Setup the plot
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots(figsize=(10, 6))

def update_plot():
    ax.clear()  # Clear the axis
    ax.plot(timestamps, prices, label="Dogecoin Price (USD)", marker='o', color='blue')

    # Add moving average if there are enough data points
    if len(prices) > 5:
        sma = np.convolve(prices, np.ones(5) / 5, mode='valid')  # Simple Moving Average
        ax.plot(timestamps[4:], sma, label="5-Point Moving Average", color='orange', linestyle='--')

    # Highlight highest and lowest points
    max_price = max(prices)
    min_price = min(prices)
    max_time = timestamps[prices.index(max_price)]
    min_time = timestamps[prices.index(min_price)]
    ax.annotate(f"Highest: ${max_price:.2f}", xy=(max_time, max_price), xytext=(max_time, max_price + 0.1),
                arrowprops=dict(facecolor='green', shrink=0.05), fontsize=10)
    ax.annotate(f"Lowest: ${min_price:.2f}", xy=(min_time, min_price), xytext=(min_time, min_price - 0.1),
                arrowprops=dict(facecolor='red', shrink=0.05), fontsize=10)

    # Format x-axis with timestamps
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45)

    ax.set_title("Real-Time Dogecoin Price (USD)", fontsize=16)
    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel("Price (USD)", fontsize=12)
    ax.legend()
    ax.grid(True)
    plt.draw()

# Real-time plotting loop
try:
    while True:
        print("Fetching real-time data...")
        price, timestamp = fetch_real_time_data()
        if price is not None and timestamp is not None:
            prices.append(price)
            timestamps.append(timestamp)

            # Update plot with new data
            update_plot()
            plt.pause(1)  # Update the graph in real-time
        else:
            print("Failed to fetch data. Skipping update.")

        print("Updating chart in 60 seconds...")
        sleep(60)
except KeyboardInterrupt:
    print("Real-time data fetching interrupted.")
    plt.ioff()
    plt.show()