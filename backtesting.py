import pandas as pd
import numpy as np
from binance.client import Client

def download_data(name_base, name_quote, timeframe, starting_date, ending_date):
    info = Client().get_historical_klines(name_base + name_quote, timeframe, starting_date, ending_date)
    data = pd.DataFrame(info, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
    data.drop(columns=data.columns.difference(['timestamp', 'close']), inplace=True)
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data['close'] = pd.to_numeric(data['close'])
    return data

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def backtest_strategy(data):
    initial_bank = 1000
    bank = initial_bank
    holdings = 0
    buy_price = 0
    max_drawdown = 0
    wins = 0
    losses = 0
    first_tp_perc = 0.75
    sec_tp_perc = 1.75
    first_sl_perc = -2
    sec_sl_perc = -3
    rsi_value_1 = 55
    rsi_value_2 = 62.5
    buy_rsi_1 = 29
    buy_rsi_2 = 27.5
    buy_rsi_3 = 26
    
    for index, row in data.iterrows():
        rsi = row['RSI']
        price = row['close']

        # Check for buy signals
        if holdings == 0:
            if rsi < buy_rsi_1:
                buy_amount = bank * 0.3
            elif rsi < buy_rsi_2:
                buy_amount = bank * 0.5
            elif rsi < buy_rsi_3:
                buy_amount = bank
            else:
                continue

            # Update bank and holdings
            bank -= buy_amount
            holdings += buy_amount / price
            buy_price = price

        # Check for sell signals
        if holdings > 0:
            profit_percent = (price - buy_price) / buy_price * 100

            # First sell condition
            if profit_percent >= first_tp_perc or rsi > rsi_value_1:
                sell_amount = holdings * 0.7
                bank += sell_amount * price
                holdings -= sell_amount

            # Second sell condition
            if profit_percent >= sec_tp_perc or rsi > rsi_value_2:
                bank += holdings * price
                holdings = 0

        # Check for stop loss conditions
        loss_percent = (price - buy_price) / buy_price * 100

        if loss_percent <= first_sl_perc:
            sell_amount = holdings * 0.7
            bank += sell_amount * price
            holdings -= sell_amount

        if loss_percent <= sec_sl_perc:
            bank += holdings * price
            holdings = 0

        # Calculate profit or loss percent
        profit_loss_percent = (price - buy_price) / buy_price * 100 if buy_price != 0 else 0

        # Update wins based on sell conditions
        if profit_loss_percent >= first_tp_perc or rsi > rsi_value_1:
            wins += 1
        if profit_loss_percent >= sec_tp_perc or rsi > rsi_value_2:
            wins += 1

        # Update losses based on stop-loss conditions
        if profit_loss_percent <= first_sl_perc:
            losses += 1
        if profit_loss_percent <= sec_sl_perc:
            losses += 1
            
        # Calculate drawdown
        current_drawdown = (price - buy_price) / buy_price * 100 if buy_price != 0 else 0
        max_drawdown = min(max_drawdown, current_drawdown)

            
    # Calculate final profit or loss and WinRate
    final_bank = bank + (holdings * data.iloc[-1]['close'])
    profit_loss = final_bank - initial_bank
    winrate = wins / (wins + losses) if (wins + losses) > 0 else 0
    roi = (final_bank - initial_bank) / initial_bank
    
    return profit_loss, winrate, wins, losses, max_drawdown, roi, initial_bank, first_tp_perc, sec_tp_perc, first_sl_perc, sec_sl_perc, rsi_value_1, rsi_value_2, buy_rsi_1, buy_rsi_2, buy_rsi_3

def save_results(pair, timeframe, starting_date, end_date, initial_bank, profit_loss, roi, winrate, wins, losses, max_drawdown,  first_tp_perc, sec_tp_perc, first_sl_perc, sec_sl_perc, rsi_value_1, rsi_value_2, buy_rsi_1, buy_rsi_2, buy_rsi_3):
    if roi > 0.50 and winrate > 0.70:
        with open('best_assets.txt', 'a') as file:
            file.write(f"Pair: {pair}\n")
            file.write(f'Timeframe: {timeframe}\n')
            file.write(f'Starting date: {starting_date}\n')
            file.write(f'End date: {end_date}\n')
            file.write(f'Initial Bank: {initial_bank}\n')
            file.write(f"Final Profit/Loss: {profit_loss}\n")
            file.write(f"ROI: {roi*100}%\n")
            file.write(f"Win Rate: {winrate*100}%\n")
            file.write(f"Wins: {wins}, Losses: {losses}\n")
            file.write(f"Max Drawdown: {max_drawdown}%\n")
            file.write(f'RSI values for the buys:\n')
            file.write(f'First buy at RSI value: {buy_rsi_1}\n')
            file.write(f'Second buy at RSI value: {buy_rsi_2}\n')
            file.write(f'Third buy at RSI value: {buy_rsi_3}\n')
            file.write(f'Values in TPs:\n')
            file.write(f'First TP percentage: {first_tp_perc}%\n')
            file.write(f'Second TP percentage: {sec_tp_perc}%\n')
            file.write(f'First RSI TP value: {rsi_value_1}\n')
            file.write(f'Second RSI TP value: {rsi_value_2}\n')
            file.write(f'Values in SLs:\n')
            file.write(f'First SL percentage: {first_sl_perc}%\n')
            file.write(f'Second SL percentage: {sec_sl_perc}%\n')
            file.write(f"---------------------------------\n\n")


# Load historical data for the cryptocurrency
timeframe = "1m"
starting_date = "15 November 2022"
end_date = "15 November 2023"
data = download_data("AVAX", "USDT", timeframe, starting_date, end_date)
data['RSI'] = calculate_rsi(data['close'])

# Run backtest
pair = "AVAX/USDT" #Change the pair name here and when you download the data, they will have to match
result, winrate, wins, losses, max_drawdown, roi, initial_bank, first_tp_perc, sec_tp_perc, first_sl_perc, sec_sl_perc, rsi_value_1, rsi_value_2, buy_rsi_1, buy_rsi_2, buy_rsi_3 = backtest_strategy(data)
print(f"Final Profit/Loss: {result}")
print(f"TimeFrame: {timeframe}")
print(f"Starting date: {starting_date}")
print(f"End date: {end_date}")
print(f"ROI: {roi*100}%")
print(f"WinRate: {winrate*100}%")
print(f"Wins: {wins}, Losses: {losses}")
print(f"Max Drawdown: {max_drawdown}%")
save_results(pair, timeframe, starting_date, end_date, initial_bank, result, roi, winrate, wins, losses, max_drawdown, first_tp_perc, sec_tp_perc, first_sl_perc, sec_sl_perc, rsi_value_1, rsi_value_2, buy_rsi_1, buy_rsi_2, buy_rsi_3)

