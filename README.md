# Python-Trading-Bot
A trading bot script made in Python to backtest a RSI strategy focused on scalping in the 1-5m timeframes with high W/R in Spot markets.

The strategy is simple, it uses the Binance.client library to access real-time data of the asset to analyze, you can install it running this command:

```
pip install python-binance
```
The script also uses the numpy and pandas libraries, you can install them using these commands:

```
pip install pandas
pip install numpy
```

The calculate_rsi() function calculates the value of RSI to use it in the strategy. 
Backtest_strategy() uses the following parameters:
Inital bank, which is the money the user will use for testing the strategy.
Percentages for TPs, where the user will adjust them depending on the asset they want to test the strategy on.
Percentages for SLs, very important to keep the drawdown low and maintain a management risk and security on the position/bank balance. Depending on the asset and risk management of the user, the SLs will be higher or lower.
RSI values for buys, the user will set these values depending on where the bot will start executing the trades, which also depends on the asset and timeframe used.
RSI values for TPs, is if the percentage for TPs doesn't reach their targets but does trigger the value of RSI TPs, a sell trade will be executed to avoid loss on profits or on the position. I will explain later on why this is necessary.

With that been said, lets move on the explanation of how the strategy works:
The user will choose an asset to analyze, change the parameters adjusted to his risk management. I'll give you an example to be clearer.
Lets look at AVAX/USDT for example, in the 1min timeframe and with these parameters:
Initial Bank: 1000
RSI values for the buys:
First buy at RSI value: 29
Second buy at RSI value: 27.5
Third buy at RSI value: 26
Values in TPs:
First TP percentage: 0.75%
Second TP percentage: 1.75%
First RSI TP value: 55
Second RSI TP value: 65
Values in SLs:
First SL percentage: -2%
Second SL percentage: -3%
The bot executes 3 buy trades, the first one with 30% of the bank whenever the RSI on the 1min timeframe goes below 29, always after closure of the previous candle. The second on if the RSI goes below 27.5 with 50% of the remaining bank balance and the last buy would be if RSI value goes below 26.
If the RSI value of the previous candle is 29.6 for example and the next one is 25.7, the bot goes full position in that candle because it has triggered all buy parameters. This is the code section for the buy signals:

<img width="274" alt="image" src="https://github.com/asier13/Python-Trading-Bot/assets/62717613/85bcc8ce-c93f-4258-9a7b-fd26ee80d7ca">

And this is an example of how it would look in the chart:

<img width="811" alt="image" src="https://github.com/asier13/Python-Trading-Bot/assets/62717613/ecc59390-96a1-4b0a-9f8f-20e52a63ac00">

The bot has triggered the first 2 buy signals, after that it keeps on calculating the RSI and now calculates the percentage of profit/loss of the position. The TPs now depends on the percentage and RSI profit of the position set by the user.
The RSI is an oscillator that measures the speed and change of price movements, supply and demand zones basically. Whenever the RSI drops below 30 it indicates the asset is oversold and usually tends have a bounce, depending on the timeframe it would be stronger or longer.
If it goes over 70, it means the asset is overbought and there is usually a rejection in the price. I use the term "usually" because the assets dont always act like that, depends on the trend, news or other factors that may impact the price action.
Now that we understand what the RSI is and how it works, let me explain how the TPs work. 
The bot bought at $21.77 and now waits for another buy oportunity or for the TP parameters to be triggered. Sometimes we dont reach the percentages TPs, so to avoid touching the SL, the RSI TPs help us get out with profit and maybe re-enter afterwards.

<img width="817" alt="image" src="https://github.com/asier13/Python-Trading-Bot/assets/62717613/007fadf7-d974-420f-b2fe-9ef44fa64fc1">

In this case, the bot triggered the first TP because the position's PNL is higher than 0.75%, which is the first percentage TP, eventhough the RSI value is 53 and our first RSI TP was 55. So we got higher PNL than the parameter we had.
After that, we are still holding 30% of the position, because with the first TP parameters we sell 70% of the position, the other 30% will be triggered or holded and added to a new position later on. In that case the second TP was triggered, getting 2.4% on that 30% remaining plus the 0.8% got in the first TP:

<img width="802" alt="image" src="https://github.com/asier13/Python-Trading-Bot/assets/62717613/bb55435d-129a-499e-ae4c-affe317581e9">

Lets take a look at another example, where the bot goes full position and sell the whole position:

<img width="804" alt="image" src="https://github.com/asier13/Python-Trading-Bot/assets/62717613/8cd7ce85-08aa-412a-a765-4bb5b4c5fbf6">

This is because the RSI closed below 26 and all buy entries where triggered, same with the TPs where the first one was when it closed with a 1% profit and second one because the RSI of the previous candle (marked with the second green line) above 65. If the bot didnt close, we would have touched the SL.
This is the reason why we use the RSI in the buys and with the TPs, to secure profits and not depend on percentages. Here is the code for the TPs section:

<img width="442" alt="image" src="https://github.com/asier13/Python-Trading-Bot/assets/62717613/815e7765-4335-459c-952a-37b194c081c2">

The buys are set at those RSI values for a reason, the bounces that we are looking for in this strategy are more likely in that 29-26 RSI value zone, giving us more W/R and more ROI because we get a better entry.
Here is an example if we set the RSI values at 31 or 30 for example marked with circles that proof that we would have a lower W/R and higher drawdown:

<img width="809" alt="image" src="https://github.com/asier13/Python-Trading-Bot/assets/62717613/4b671dca-c464-4fdc-850e-90532a38b330">

Last example to explain how we would hold the position and understand how the SL works in this strategy.
So for the first scenario, sometimes the RSI value will go below 26 which is my last buy trade but we wouldnt get the bounce we want, but because we are trading on lower timeframes, we would have to wait for the higher timeframes to do the work for us.
Here we would go full position as the RSI goes below 26 but we will only get a 0.55% bounce and RSI doesnt even reach 45, which is not enough to trigger our TPs. Price keeps falling and the bot just waits for TPs or the SLs. 

<img width="809" alt="image" src="https://github.com/asier13/Python-Trading-Bot/assets/62717613/8a9163f0-86b3-4032-8203-799f9f64eec0">

The lowest it gets is -1.28%, which is far from our first SL in -2% and the bot keeps waiting. But the bounce comes and the RSI values trigger the RSI TPs, first at 55 and later on, at 65. These TPs in this situation act as SL because the PNL when the RSI is at 55 is at -0.25% and when it gets to 65 its basically B/E.
For cases with strong downtrend and no bounces its very important to have a SL to avoid losing our capital, so here is an example, where price is falling heavy and we go full position, but the SL gets triggered as we fall below our -2% SL:

<img width="814" alt="image" src="https://github.com/asier13/Python-Trading-Bot/assets/62717613/ab7f8915-9cdd-4296-95fc-3011e73153d5">

Because we are full position, the bot cant keep adding trades, so it has to wait for the price to bounce or the SLs. For the first SL we sell 70% of the position at a -2% loss, the percentage depends on the asset and risk management of the user as I said at the beginning.
The bot as soon as it sells, it triggers a buy and goes full position again because the previous candle closed with a RSI value below 26, averaging the position and again, wait for new trades, either the TPs or SLs to get triggered, in that case it was the TPs:

<img width="814" alt="image" src="https://github.com/asier13/Python-Trading-Bot/assets/62717613/043a0c29-7192-42f1-9433-027bf0e37112">

If the price continued dropping and the PNL went below -3%, the bot will sell the entire position and will wait for next buying opportunities.

When the analysis is finished, the bot stores the best assets with a ROI over 50% and a W/R over 70%, saving the values of the parameters used, the date the user used to analyze the PA of the asset using the strategy, the initial bank, roi, W/R and drawdown.

I hope you appreciate the work and the analysis. This is NFA and DYOR as always. Have fun with it!



