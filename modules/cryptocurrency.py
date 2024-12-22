import requests


# Function to get real-time price from CoinGecko
def get_price(crypto_id='bitcoin', currency='usd'):
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies={currency}'

    # Sending a GET request to the CoinGecko API
    response = requests.get(url)

    # Check if the response is successful
    if response.status_code == 200:
        data = response.json()
        price = data.get(crypto_id, {}).get(currency)
        if price:
            print(f"The current price of {crypto_id} in {currency} is {price}")
        else:
            print(f"Could not retrieve price for {crypto_id}.")
    else:
        print(f"Error: Unable to fetch data (Status code: {response.status_code})")


# Example usage: Get Bitcoin price in USD
get_price('dogecoin', 'usd')

# Example usage: Get Ethereum price in EUR
get_price('dogecoin', 'eur')
