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
    initial_bank = 1000 #The inital bank that the user will use
    bank = initial_bank
    holdings = 0
    buy_price = 0
    max_drawdown = 0
    wins = 0
    losses = 0
    first_tp_perc = 1 #Values for TPs
    sec_tp_perc = 1.5
    sl_perc = -2 #Value for SL
    rsi_value_1 = 42.5 #Values for TPs in the RSI
    rsi_value_2 = 55
    buy_rsi_1 = 29.5 #Values for buys in the RSI
    buy_rsi_2 = 28.5
    buy_rsi_3 = 27
   # Flags to track if a buy level and TP1 has been triggered 
    bought_buy_1 = False
    bought_buy_2 = False
    bought_buy_3 = False
    tp_1_hit = False

    for index, row in data.iterrows():
        rsi = row['RSI']
        price = row['close']
        buy_amount = 0
        profit_percent = 0
        
        # Check for buy signals
        if holdings == 0 or (holdings > 0 and tp_1_hit):
            if rsi < buy_rsi_1 and not bought_buy_1:
                buy_amount = bank * (0.25 if tp_1_hit else 0.4) # If TP1 was hit, we lower the bank amount invested if RSI goes below buy_rsi_1 again
                bought_buy_1 = True
                bank -= buy_amount
                holdings += buy_amount / price
                buy_price = price if holdings == buy_amount / price else buy_price
            elif rsi < buy_rsi_2 and not bought_buy_2:
                buy_amount = bank * 0.5
                bought_buy_2 = True
                bank -= buy_amount
                holdings += buy_amount / price
                buy_price = price if holdings == buy_amount / price else buy_price
            elif rsi < buy_rsi_3 and not bought_buy_3:
                buy_amount = bank
                bought_buy_3 = True
                bank -= buy_amount
                holdings += buy_amount / price
                buy_price = price if holdings == buy_amount / price else buy_price

            # Update bank and holdings if a buy signal was triggered
            if buy_amount > 0:
                bank -= buy_amount
                holdings += buy_amount / price
                buy_price = price if holdings == buy_amount / price else buy_price

        # Check for sell signals
        if holdings > 0:
            profit_percent = (price - buy_price) / buy_price * 100
            # First sell condition(TP1)
            if profit_percent >= first_tp_perc or rsi > rsi_value_1:
                sell_amount = holdings * 0.8
                bank += sell_amount * price
                holdings -= sell_amount
                bought_buy_1 = False
                bought_buy_2 = False
                bought_buy_3 = False
                tp_1_hit = True
                if profit_loss_percent > 0: 
                    wins += 1
                else: 
                    losses += 1

            # Second sell condition(TP2)
            if profit_percent >= sec_tp_perc or rsi > rsi_value_2:
                sell_amount = holdings
                bank += sell_amount * price
                holdings = 0
                bought_buy_1 = False
                bought_buy_2 = False
                bought_buy_3 = False
                if profit_loss_percent > 0: 
                    wins += 1
                else: 
                    losses += 1
                        
            if tp_1_hit and (rsi > rsi_value_2):
                bought_buy_1 = False
                bought_buy_2 = False
                bought_buy_3 = False
                tp_1_hit = False
                
        # Check for stop loss conditions only if we have holdings
        if holdings > 0:
            loss_percent = (price - buy_price) / buy_price * 100
            if loss_percent <= sl_perc:
                sell_amount = holdings
                bank += sell_amount * price
                holdings = 0
                bought_buy_1 = False
                bought_buy_2 = False
                bought_buy_3 = False
                tp_1_hit = False  
                losses += 1  # Increment losses when we hit stop loss

        # Update wins and losses based on sell conditions and actual PnL
        profit_loss_percent = (price - buy_price) / buy_price * 100 if buy_price != 0 else 0
        
        if (profit_percent >= first_tp_perc or rsi > rsi_value_1) and profit_loss_percent > 0:
            wins += 1
        elif (profit_percent >= first_tp_perc or rsi > rsi_value_1) and profit_loss_percent <= 0:
            losses += 1

        if (profit_percent >= sec_tp_perc or rsi > rsi_value_2) and profit_loss_percent > 0:
            wins += 1
        elif (profit_percent >= sec_tp_perc or rsi > rsi_value_2) and profit_loss_percent <= 0:
            losses += 1

            
        # Calculate drawdown
        current_drawdown = (price - buy_price) / buy_price * 100 if buy_price != 0 else 0
        max_drawdown = min(max_drawdown, current_drawdown)

            
    # Calculate final profit or loss and WinRate
    final_bank = bank + (holdings * data.iloc[-1]['close'])
    profit_loss = final_bank - initial_bank
    winrate = wins / (wins + losses) if (wins + losses) > 0 else 0
    roi = (final_bank - initial_bank) / initial_bank
    
    return profit_loss, winrate, wins, losses, max_drawdown, roi, initial_bank, first_tp_perc, sec_tp_perc, sl_perc, rsi_value_1, rsi_value_2, buy_rsi_1, buy_rsi_2, buy_rsi_3

def save_results(pair, timeframe, starting_date, end_date, initial_bank, profit_loss, roi, winrate, wins, losses, max_drawdown,  first_tp_perc, sec_tp_perc, sl_perc, rsi_value_1, rsi_value_2, buy_rsi_1, buy_rsi_2, buy_rsi_3):
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
            file.write(f'Value in SL:\n')
            file.write(f'SL percentage: {sl_perc}%\n')
            file.write(f"---------------------------------\n\n")


# Load historical data for the cryptocurrency
timeframe = "5m"
starting_date = "1 January 2022"
end_date = "15 November 2023"
data = download_data("QNT", "USDT", timeframe, starting_date, end_date)
data['RSI'] = calculate_rsi(data['close'])

# Run backtest
result, winrate, wins, losses, max_drawdown, roi, initial_bank, first_tp_perc, sec_tp_perc, sl_perc, rsi_value_1, rsi_value_2, buy_rsi_1, buy_rsi_2, buy_rsi_3 = backtest_strategy(data)
print(f"Pair: {pair}")
print(f"Final Profit/Loss: {result}")
print(f"TimeFrame: {timeframe}")
print(f"Starting date: {starting_date}")
print(f"End date: {end_date}")
print(f"ROI: {roi*100}%")
print(f"WinRate: {winrate*100}%")
print(f"Wins: {wins}, Losses: {losses}")
print(f"Max Drawdown: {max_drawdown}%")
save_results(pair, timeframe, starting_date, end_date, initial_bank, result, roi, winrate, wins, losses, max_drawdown, first_tp_perc, sec_tp_perc, sl_perc, rsi_value_1, rsi_value_2, buy_rsi_1, buy_rsi_2, buy_rsi_3)

