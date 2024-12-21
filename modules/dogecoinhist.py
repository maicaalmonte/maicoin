import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# CryptoCompare API endpoint without requiring an API key
url = "https://min-api.cryptocompare.com/data/v2/histoday"
params = {
    'fsym': 'DOGE',           # Cryptocurrency (Dogecoin)
    'tsym': 'USD',            # Target currency (USD)
    'limit': 100,             # Number of days of data to retrieve (100 days)
}

# Function to fetch historical data
def fetch_cryptocompare_data():
    try:
        # Calculate the timestamp for 100 days ago
        to_date = datetime(2024, 12, 19)  # Start date: January 1, 2019
        from_timestamp = int(to_date.timestamp())  # Convert to timestamp

        params['toTs'] = from_timestamp  # Set the 'to' timestamp for 2019 start date

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if 'Data' not in data or 'Data' not in data['Data']:
            print("No data returned by the API.")
            return None

        # Convert data to DataFrame
        df = pd.DataFrame(data['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')  # Convert UNIX time to datetime
        df['close'] = pd.to_numeric(df['close'])

        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Fetch historical data
data = fetch_cryptocompare_data()

if data is not None:
    # Plotting the data
    plt.figure(figsize=(10, 6))
    plt.plot(data['time'], data['close'], label="Dogecoin Price (USD)", color='blue')

    # Format the x-axis for date/time
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45)

    plt.title("Dogecoin Historical Data (CryptoCompare)", fontsize=16)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Price (USD)", fontsize=12)
    plt.legend()
    plt.grid(True)
    plt.show()
else:
    print("No data available.")
