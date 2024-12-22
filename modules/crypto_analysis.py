import requests
import pandas as pd
import datetime
import logging
from time import sleep

# Setup logging configuration
logging.basicConfig(level=logging.INFO)


def fetch_crypto_data(crypto_id, currency='usd', hours=48):
    """
    Fetch historical market data for the given cryptocurrency using the CoinGecko API.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart/range"
    end_time = int(datetime.datetime.now().timestamp())
    start_time = end_time - hours * 3600  # Last 'hours' hours

    params = {
        'vs_currency': currency,
        'from': start_time,
        'to': end_time
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Will raise an HTTPError for bad status codes
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data for {crypto_id}: {e}")
        raise Exception(f"Failed to fetch data for {crypto_id}: {e}")

    return response.json()


def analyze_best_trading_opportunities(crypto_data):
    """
    Analyze the best time to buy and sell based on hourly average prices.
    """
    if "prices" not in crypto_data or not crypto_data["prices"]:
        raise ValueError("No price data available for analysis.")

    prices = crypto_data["prices"]
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Grouping by hour and computing average price
    df['hour'] = df['date'].dt.hour
    current_hour = datetime.datetime.now().hour
    df = df[df['hour'] != current_hour]  # Exclude current hour

    # Compute hourly average prices
    hourly_avg_prices = df.groupby('hour')['price'].mean()

    # Handle case where there might be NaN values
    hourly_avg_prices = hourly_avg_prices.fillna(0)  # Replace NaN with 0 (or use other strategies)

    best_buy_hour = hourly_avg_prices.idxmin()  # Best hour to buy (min price)
    best_sell_hour = hourly_avg_prices.idxmax()  # Best hour to sell (max price)

    # Log and return the results
    logging.info(f"Best Buy Hour: {best_buy_hour} at price {hourly_avg_prices[best_buy_hour]}")
    logging.info(f"Best Sell Hour: {best_sell_hour} at price {hourly_avg_prices[best_sell_hour]}")

    return {
        'hourly_avg_prices': hourly_avg_prices.to_dict(),
        'best_buy_hour': best_buy_hour,
        'best_sell_hour': best_sell_hour,
        'best_buy_price': hourly_avg_prices[best_buy_hour],
        'best_sell_price': hourly_avg_prices[best_sell_hour]
    }


def analyze_multiple_cryptos(crypto_ids, currency='usd', hours=48):
    """
    Fetch and analyze best trading opportunities for multiple cryptocurrencies.
    """
    analysis_results = {}
    for crypto_id in crypto_ids:
        logging.info(f"Fetching data and analyzing for {crypto_id}")
        try:
            # Fetch data
            crypto_data = fetch_crypto_data(crypto_id, currency, hours)

            if crypto_data:
                # Analyze trading opportunities
                analysis = analyze_best_trading_opportunities(crypto_data)
                analysis_results[crypto_id] = analysis
            else:
                logging.warning(f"No data returned for {crypto_id}.")

            # Add a delay to avoid overloading the API
            sleep(2)  # Wait for 2 seconds before the next API call
        except Exception as e:
            logging.error(f"An error occurred for {crypto_id}: {e}")

    return analysis_results


if __name__ == "__main__":
    crypto_ids = ["bitcoin", "ethereum", "dogecoin"]  # List of cryptocurrencies to analyze
    currency = "usd"
    hours = 48  # Set the number of hours for fetching data

    try:
        # Analyze multiple cryptocurrencies
        results = analyze_multiple_cryptos(crypto_ids, currency, hours)
        print(results)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
