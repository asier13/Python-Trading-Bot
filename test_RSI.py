import pandas as pd
from binance.client import Client
from binance.enums import *

def calculate_rsi(data, periods=14):
    delta = data['close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=periods, min_periods=periods).mean()[:periods+1]
    avg_loss = loss.rolling(window=periods, min_periods=periods).mean()[:periods+1]

    for i in range(periods, len(delta)):
        avg_gain.loc[i] = (avg_gain[i-1] * (periods-1) + gain[i]) / periods
        avg_loss.loc[i] = (avg_loss[i-1] * (periods-1) + loss[i]) / periods

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Initialize Binance Client
client = Client()

# Fetch historical data
klines = client.get_historical_klines("QNTUSDT", Client.KLINE_INTERVAL_5MINUTE, "12 hours ago UTC")

# Create DataFrame
df = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
df['close'] = pd.to_numeric(df['close'])

# Calculate RSI
df['RSI'] = calculate_rsi(df)

# Display the last RSI value
print(df['RSI'].iloc[-1])

