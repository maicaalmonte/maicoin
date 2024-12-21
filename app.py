from flask import Flask, render_template, jsonify, url_for
import importlib.util
import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__, static_folder='static')

# Ensure the 'static/img' directory exists for plot saving
plot_dir = os.path.join(app.static_folder, 'img')
os.makedirs(plot_dir, exist_ok=True)

# Load module function with logging and file path check
def load_module(module_name, file_path):
    logging.info(f"Attempting to load module {module_name} from {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"Error loading module {module_name}: File {file_path} does not exist")
        return None
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        logging.info(f"Module {module_name} loaded successfully")
        return module
    except Exception as e:
        logging.error(f"Error loading module {module_name}: {e}")
        return None

# Load your modules from the correct paths
modules = {
    "BTC": load_module("bitcoinest", "modules/bitcoinest.py"),
    "BTC_HIST": load_module("bitcoinhist", "modules/bitcoinhist.py"),
    "BTC_REAL": load_module("bitcoinreal", "modules/bitcoinreal.py"),
    "DOGE": load_module("dogecoinest", "modules/dogecoinest.py"),
    "DOGE_HIST": load_module("dogecoinhist", "modules/dogecoinhist.py"),
    "DOGE_REAL": load_module("dogecoinreal", "modules/dogecoinreal.py"),
    "ETH": load_module("ethereumest", "modules/ethereumest.py"),
    "ETH_HIST": load_module("ethereumhist", "modules/ethereumhist.py"),
    "ETH_REAL": load_module("ethereumreal", "modules/ethereumreal.py"),
}

# Function to fetch data for each module (every x minutes)
def fetch_data_for_modules():
    logging.info("Fetching data for all modules")
    for module_key, module in modules.items():
        try:
            if module and hasattr(module, 'get_data'):
                data = module.get_data()
                if data and 'prices' in data:
                    logging.info(f"Fetched new data for {module_key}: {data['prices']}")
                else:
                    logging.warning(f"No data found for {module_key}")
        except Exception as e:
            logging.error(f"Error fetching data for {module_key}: {e}")

# Set up background scheduler to fetch data every 5 minutes
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(fetch_data_for_modules, 'interval', minutes=5)
scheduler.start()

# Generic function to fetch data for a given route
def get_data_for_route(module_key):
    logging.info(f"Getting data for route: {module_key}")
    try:
        module = modules.get(module_key)
        if module and hasattr(module, 'get_data'):
            data = module.get_data()
            logging.info(f"Data for {module_key}: {data}")
            if not data or 'prices' not in data:
                return {"error": f"No data available for {module_key}"}
            return data
        else:
            return {"error": f"Module {module_key} not found"}
    except Exception as e:
        logging.error(f"Error getting data for {module_key}: {e}")
        return {"error": f"Failed to fetch data for {module_key}"}

# Routes for different pages
@app.route('/')
def home():
    logging.info('Home route accessed')
    return render_template('index.html')

@app.route('/bitcoin')
def bitcoin():
    logging.info('Bitcoin route accessed')
    btc_data = get_data_for_route('BTC')

    if btc_data.get('error'):
        logging.error(f"Error in BTC data: {btc_data.get('error')}")
        return render_template('bitcoin.html', data=btc_data)

    plot_url = url_for('static', filename='img/bitcoin_plot.png')
    best_times = {
        "best_buy_hour": 1,
        "lowest_price": 20000,
        "best_sell_hour": 2,
        "highest_price": 21000
    }
    return render_template('bitcoin.html', data=btc_data, plot_url=plot_url, best_times=best_times)

@app.route('/dogecoin')
def dogecoin():
    logging.info('Dogecoin route accessed')
    doge_data = get_data_for_route('DOGE')

    if doge_data.get('error'):
        logging.error(f"Error in DOGE data: {doge_data.get('error')}")
        return render_template('dogecoin.html', data=doge_data)

    plot_url = url_for('static', filename='img/dogecoin_plot.png')
    best_times = {
        "best_buy_hour": 1,
        "lowest_price": 0.05,
        "best_sell_hour": 2,
        "highest_price": 0.06
    }
    return render_template('dogecoin.html', data=doge_data, plot_url=plot_url, best_times=best_times)

@app.route('/ethereum')
def ethereum():
    logging.info('Ethereum route accessed')
    eth_data = get_data_for_route('ETH')

    if eth_data.get('error'):
        logging.error(f"Error in ETH data: {eth_data.get('error')}")
        return render_template('ethereum.html', data=eth_data)

    plot_url = url_for('static', filename='img/ethereum_plot.png')
    best_times = {
        "best_buy_hour": 1,
        "lowest_price": 1500,
        "best_sell_hour": 2,
        "highest_price": 1600
    }
    return render_template('ethereum.html', data=eth_data, plot_url=plot_url, best_times=best_times)

@app.route('/realtime_bitcoin_data')
def realtime_bitcoin_data():
    logging.info('Realtime Bitcoin Data route accessed')
    btc_data = get_data_for_route('BTC')

    if btc_data.get('error'):
        return jsonify(error=btc_data.get('error'))

    best_times = {
        "best_buy_hour": 1,
        "lowest_price": 20000,
        "best_sell_hour": 2,
        "highest_price": 21000
    }
    return jsonify(dates=btc_data['dates'], prices=btc_data['prices'], best_times=best_times)

if __name__ == '__main__':
    try:
        logging.info("Flask app is about to start")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        logging.error(f"Error occurred while starting the app: {e}", exc_info=True)