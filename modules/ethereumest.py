import requests
import pandas as pd
import datetime

# CoinGecko API endpoint for historical market data
url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart/range"

# Define the time range (e.g., last 48 hours)
# You'll need to convert the start and end times to Unix timestamps
end_time = int(datetime.datetime.now().timestamp())
start_time = end_time - 48 * 3600  # Last 48 hours

params = {
    'vs_currency': 'usd',
    'from': start_time,
    'to': end_time
}

response = requests.get(url, params=params)
data = response.json()

# Get the price data (timestamps and prices)
prices = data['prices']

# Convert to DataFrame
df = pd.DataFrame(prices, columns=['timestamp', 'price'])

# Convert the timestamp to readable date
df['date'] = pd.to_datetime(df['timestamp'], unit='ms')

# Extract hour from the timestamp
df['hour'] = df['date'].dt.hour

# Exclude the current hour from the analysis
current_hour = datetime.datetime.now().hour
df = df[df['hour'] != current_hour]

# Calculate average price for each hour
hourly_avg_prices = df.groupby('hour')['price'].mean()

# Find the best time to buy (lowest price) and sell (highest price)
best_buy_hour = hourly_avg_prices.idxmin()
best_sell_hour = hourly_avg_prices.idxmax()

# Print hourly average prices
print("Average Prices by Hour (Excluding Current Hour):")
print(hourly_avg_prices)

print("\nBest time to buy:")
print(f"Hour {best_buy_hour}: {hourly_avg_prices[best_buy_hour]:.2f} USD (Lowest average price)")

print("\nBest time to sell:")
print(f"Hour {best_sell_hour}: {hourly_avg_prices[best_sell_hour]:.2f} USD (Highest average price)")
