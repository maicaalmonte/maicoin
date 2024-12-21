import requests
from time import sleep
import datetime

# Define the URL and parameters for Dogecoin data from CoinGecko
url = "https://api.coingecko.com/api/v3/coins/dogecoin/market_chart/range"
params = {
    'vs_currency': 'usd',
    'from': 1734386278,  # Example timestamp (start date)
    'to': 1734559078     # Example timestamp (end date)
}

# Function to analyze the best trading opportunities
def analyze_trading_opportunities(data):
    if "prices" not in data:
        print("No price data available for analysis.")
        return

    prices = data["prices"]  # List of [timestamp, price] pairs
    if not prices:
        print("Price data is empty.")
        return

    # Initialize variables for analysis
    min_price = float('inf')
    max_profit = 0
    buy_time = None
    sell_time = None
    best_buy_price = None
    best_sell_price = None

    for timestamp, price in prices:
        # Track the lowest price encountered so far
        if price < min_price:
            min_price = price
            buy_time = timestamp
            best_buy_price = price

        # Calculate potential profit if sold at the current price
        profit = price - min_price
        if profit > max_profit:
            max_profit = profit
            sell_time = timestamp
            best_sell_price = price

    # Print analysis results
    if max_profit > 0:
        print("\n--- Best Trading Analysis ---")
        print(f"Best Buy Time: {datetime.datetime.utcfromtimestamp(buy_time / 1000)} at ${best_buy_price:.2f}")
        print(f"Best Sell Time: {datetime.datetime.utcfromtimestamp(sell_time / 1000)} at ${best_sell_price:.2f}")
        print(f"Maximum Profit: ${max_profit:.2f}")
    else:
        print("\nNo profitable trading opportunities found in the given data range.")

# Retry logic with delay in case of failure
retries = 5
for attempt in range(retries):
    try:
        # Send a GET request to CoinGecko API with timeout
        print(f"Fetching data... Attempt {attempt + 1}/{retries}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        print("Data fetched successfully!")

        # Perform trading analysis
        analyze_trading_opportunities(data)
        break  # Exit the loop if the request is successful
    except requests.exceptions.RequestException as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt < retries - 1:
            print("Retrying in 2 seconds...")
            sleep(2)  # Wait for 2 seconds before retrying
        else:
            print("Max retries reached. Could not fetch data.")
