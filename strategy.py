from kucoin.client import User, Trade
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
from datetime import datetime
import time
import pytz

# KuCoin API credentials
api_key = 'your_api_key'
api_secret = 'your_api_secret'
api_passphrase = 'your_passphrase'
trade_client = Trade(key=api_key, secret=api_secret, passphrase=api_passphrase)
# KuCoin client
client = User(api_key, api_secret, api_passphrase, url='https://openapi-v2.kucoin.com')
# Ticker symbols for each exchange
binance_symbol = 'QNTUSDT'
kucoin_symbol = 'QNT-USDT'
# Custom Exception for KuCoin API
class KucoinAPIException(Exception):
    def __init__(self, status_code, message):
        super().__init__(f"Error {status_code}: {message}")

def calculate_rsi(data, periods=14, ema=True):
    # Make sure there is enough data to calculate the RSI
    if len(data) < periods:
        print(f"Not enough data to calculate RSI. Data length: {len(data)}")
        return pd.Series([float('nan')] * len(data))
    
    delta = data.diff(1)
    delta = delta[1:]

    gain = (delta.where(delta > 0, 0)).abs()
    loss = (-delta.where(delta < 0, 0)).abs()

    if ema:
        # Use the exponential moving average
        avg_gain = gain.ewm(com=periods-1, min_periods=periods, adjust=False).mean()
        avg_loss = loss.ewm(com=periods-1, min_periods=periods, adjust=False).mean()
    else:
        # Use the simple moving average
        avg_gain = gain.rolling(window=periods, min_periods=periods).mean()
        avg_loss = loss.rolling(window=periods, min_periods=periods).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def time_until_next_candle(interval_seconds):
    current_time = datetime.utcnow()
    time_elapsed_since_last_candle = current_time.timestamp() % interval_seconds
    time_until_next_candle = interval_seconds - time_elapsed_since_last_candle
    return time_until_next_candle


def convert_to_local_time(utc_time, timezone='Europe/Madrid'):
    # Convert milliseconds to seconds and then use datetime.fromtimestamp
    utc_datetime = datetime.utcfromtimestamp(utc_time / 1000.0)
    local_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(timezone))
    return local_datetime.strftime('%Y-%m-%d %H:%M:%S')

def fetch_latest_data(interval):
    client = Client()
    try:
        # Adjust this number as necessary to get at least 15 data points
        klines = client.get_klines(symbol=binance_symbol, interval=interval, limit=150)
    except BinanceAPIException as e:
        print(f"Binance API exception occurred: {e.status_code} - {e.message}")
        return pd.DataFrame()

    if not klines:
        print("No data returned from Binance API")
        return pd.DataFrame()

    data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
    data['close'] = pd.to_numeric(data['close'], errors='coerce')


    return data


def fetch_current_price():
    client = Client()
    ticker = client.get_symbol_ticker(symbol=binance_symbol)
    return float(ticker['price'])

def execute_trading_strategy(rsi_last_value, bank, holdings, buy_price, bought_buy_1, bought_buy_2, bought_buy_3, tp_1_hit):
    first_tp_perc = 1 #Values for TPs
    sec_tp_perc = 1.5
    sl_perc = -2 #Value for SL
    rsi_value_1 = 42.5 #Values for TPs in the RSI
    rsi_value_2 = 55
    buy_rsi_1 = 29.5 #Values for buys in the RSI
    buy_rsi_2 = 28.5
    buy_rsi_3 = 27
    amount_to_invest = 0 
    try:
            # Fetch latest data and calculate RSI
            rsi = rsi_last_value
            # Buy conditions
            if holdings == 0 or (holdings > 0 and tp_1_hit):
                if rsi_last_value < buy_rsi_1 and not bought_buy_1:
                    amount_to_invest = bank * (0.25 if tp_1_hit else 0.4)  # Adjusting the investment amount based on TP1 hit
 
                    # Calculate the size based on the current price and amount to invest
                    current_price = fetch_current_price()  # Implement this function to get the current price
                    size = amount_to_invest / current_price  # This gives the quantity of the asset to buy
                    try:
                        order = trade_client.create_market_order(kucoin_symbol, 'buy', size=size)
                        print(f"Buy order executed: {order}")
                        # Update bank, holdings, buy flags
                        bank -= amount_to_invest
                        holdings += size
                        bought_buy_1 = True
                    except KucoinAPIException as e:
                        print(f"Error executing buy order: {e}")


                elif rsi_last_value < buy_rsi_2 and not bought_buy_2:
                    amount_to_invest = bank * 0.5
                    # Calculate the size based on the current price and amount to invest
                    current_price = fetch_current_price()  # Implement this function to get the current price
                    size = amount_to_invest / current_price  # This gives the quantity of the asset to buy
                    try:
                        order = trade_client.create_market_order(kucoin_symbol, 'buy', size=size)
                        print(f"Buy order executed: {order}")
                        # Update bank, holdings, buy flags
                        bank -= amount_to_invest
                        holdings += size
                        bought_buy_1 = True
                    except KucoinAPIException as e:
                        print(f"Error executing buy order: {e}")

                elif rsi_last_value < buy_rsi_3 and not bought_buy_3:
                    amount_to_invest = bank
                    # Calculate the size based on the current price and amount to invest
                    current_price = fetch_current_price()  # Implement this function to get the current price
                    size = amount_to_invest / current_price  # This gives the quantity of the asset to buy
                    try:
                        order = trade_client.create_market_order(kucoin_symbol, 'buy', size=size)
                        print(f"Buy order executed: {order}")
                        # Update bank, holdings, buy flags
                        bank -= amount_to_invest
                        holdings += size
                        bought_buy_1 = True
                    except KucoinAPIException as e:
                        print(f"Error executing buy order: {e}")
                        
                # Update bank and holdings after a buy signal
                if amount_to_invest > 0:
                    bank -= amount_to_invest
                    holdings += amount_to_invest / current_price
                    buy_price = current_price if holdings == amount_to_invest / current_price else buy_price

            # Sell conditions
            if holdings > 0:
                profit_percent = (current_price - buy_price) / buy_price * 100  # Current profit percentage
                # First sell condition (TP1)
                if profit_percent >= first_tp_perc or rsi > rsi_value_1:
                    sell_amount = holdings * 0.8  # Selling 80% of holdings
                    try:
                        order = trade_client.create_market_order(kucoin_symbol, 'sell', size=sell_amount)
                        print(f"First TP sell order executed: {order}")
                        # Update holdings, bank, and flags
                        holdings -= sell_amount
                        bank += sell_amount * current_price
                        tp_1_hit = True  # Flag to indicate first TP has been hit
                    except KucoinAPIException as e:
                        print(f"Error executing first TP sell order: {e}")

                # Second sell condition (TP2)
                if profit_percent >= sec_tp_perc or rsi > rsi_value_2:
                    sell_amount = holdings  # Selling remaining holdings
                    try:
                        order = trade_client.create_market_order(kucoin_symbol, 'sell', size=sell_amount)
                        print(f"Second TP sell order executed: {order}")
                        # Resetting holdings, bank, and flags as position is fully closed
                        holdings = 0
                        bank += sell_amount * current_price
                        bought_buy_1 = False
                        bought_buy_2 = False
                        bought_buy_3 = False
                        tp_1_hit = False
                    except KucoinAPIException as e:
                        print(f"Error executing second TP sell order: {e}")


            # Stop loss conditions
            if holdings > 0:
                current_price = fetch_current_price()  # Implement this function to get the current price
                loss_percent = (current_price - buy_price) / buy_price * 100
                if loss_percent <= sl_perc:  # Assuming sl_perc is the stop loss percentage threshold
                    try:
                        order = trade_client.create_market_order(kucoin_symbol, 'sell', size=holdings)
                        print(f"Stop loss sell order executed: {order}")
                        # Update bank, holdings, and flags
                        bank += holdings * current_price
                        holdings = 0
                        bought_buy_1 = False
                        bought_buy_2 = False
                        bought_buy_3 = False
                        tp_1_hit = False
                    except KucoinAPIException as e:
                        print(f"Error executing stop loss sell order: {e}")

            
    except KucoinAPIException as e:
        print(f"API error occurred: {e}")


def main():
    interval = '5m'
    interval_seconds = 300  # 5 minutes in seconds
    bank = 1000
    holdings = 0
    buy_price = 0
    bought_buy_1 = False
    bought_buy_2 = False
    bought_buy_3 = False
    tp_1_hit = False

    print("Running the bot...")

    # Calculate the time for the next candle to close
    next_candle_time = datetime.utcnow().timestamp() + (interval_seconds - datetime.utcnow().timestamp() % interval_seconds)
    while True:
        try:
            current_time = datetime.utcnow().timestamp()
            time_until_next_candle = next_candle_time - current_time

            if time_until_next_candle <= 0:
                data = fetch_latest_data(interval)

                if not data.empty and 'close' in data.columns:
                    rsi_values = calculate_rsi(data['close'])

                    if not rsi_values.empty:
                        rsi_last_closed_candle = rsi_values.iloc[-1]
                        last_candle_close_time = data.iloc[-1]['close_time']
                        print(f'RSI at the close of last candle: {rsi_last_closed_candle:.2f}')
                        # Execute your trading strategy here
                        execute_trading_strategy(rsi_last_closed_candle, bank, holdings, buy_price, bought_buy_1, bought_buy_2, bought_buy_3, tp_1_hit)
                # Recalculate the time for the next candle
                next_candle_time = datetime.utcnow().timestamp() + (interval_seconds - datetime.utcnow().timestamp() % interval_seconds)
            else:
                print(f"Sleeping for {time_until_next_candle} seconds.")
                time.sleep(time_until_next_candle)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            time.sleep(60)  # Wait before retrying

main()