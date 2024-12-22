# api_utils.py
import requests
import logging

BASE_URL = 'https://api.coingecko.com/api/v3'

def get_prices(crypto_ids, currency='usd'):
    """Fetch prices for multiple cryptocurrencies."""
    ids = ','.join(crypto_ids)
    url = f'{BASE_URL}/simple/price?ids={ids}&vs_currencies={currency}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching prices: {e}")
        return {}
