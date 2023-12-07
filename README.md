# Python-Trading-Bot
A crypto trading bot script made in Python to backtest a RSI strategy focused on scalping in the 1-5-15m timeframes with high W/R in Spot markets.

The strategy is simple, it uses the Binance.client library to access real-time data of the asset to analyze, you can install all the requirements in the requirements.txt

The calculate_rsi() function calculates the value of RSI to use it in the strategy. 
Backtest_strategy() uses the following parameters:
Inital bank, which is the money the user will use for testing the strategy.
Percentages for TPs, where the user will adjust them depending on the asset they want to test the strategy on.
Percentages for SL, very important to keep the drawdown low and maintain a management risk and security on the position/bank balance. Depending on the asset and risk management of the user, the SL will be higher or lower.
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

Values in SL:

SL percentage: -2%


The bot executes 3 buy trades, the first one with 40% of the bank whenever the RSI on the 1min timeframe goes below 29, always after closure of the previous candle. The second on if the RSI goes below 27.5 with 50% of the remaining bank balance and the last buy would be if RSI value goes below 26.
If the RSI value of the previous candle is 29.6 for example and the next one is 25.7, the bot goes full position in that candle because it has triggered all buy parameters. This is the code section for the buy signals:

<img width="577" alt="image" src="https://github.com/asier13/Python-Trading-Bot/assets/62717613/5af641b6-a27c-405a-9064-d32bbedab8b0">


And this is an example of how it would look in the chart:

![image](https://github.com/asier13/Python-Trading-Bot/assets/62717613/82731337-9f76-4ea2-9248-cc551235ce89)


The bot has triggered the first 2 buy signals, after that it keeps on calculating the RSI and now calculates the percentage of profit/loss of the position. The TPs now depends on the percentage and RSI profit of the position set by the user.
The RSI is an oscillator that measures the speed and change of price movements, supply and demand zones basically. Whenever the RSI drops below 30 it indicates the asset is oversold and usually tends have a bounce, depending on the timeframe it would be stronger or longer.
If it goes over 70, it means the asset is overbought and there is usually a rejection in the price. I use the term "usually" because the assets dont always act like that, depends on the trend, news or other factors that may impact the price action.
Now that we understand what the RSI is and how it works, let me explain how the TPs work. 
The bot bought at $21.77 and now waits for another buy oportunity or for the TP parameters to be triggered. Sometimes we dont reach the percentages TPs, so to avoid touching the SL, the RSI TPs help us get out with profit and maybe re-enter afterwards.

![image](https://github.com/asier13/Python-Trading-Bot/assets/62717613/080371ad-084d-4ed6-a964-80b5f20c99b3)

In this case, the bot triggered the first TP because the position's PNL is higher than 0.75%, which is the first percentage TP, eventhough the RSI value is 53 and our first RSI TP was 55. So we got higher PNL than the parameter we had.
After that, we are still holding 20% of the position, because with the first TP parameters we sell 80% of the position, the other 20% will be triggered or holded and added to a new position later on. In that case the second TP was triggered, getting 2.4% on that 20% remaining plus the 0.8% got in the first TP:

![image](https://github.com/asier13/Python-Trading-Bot/assets/62717613/124a2940-6ee1-4a0e-a378-2dc8dcc99a51)

When the first TP is hit, we set the boolean value of tp_1_hit to True and reset the values of the buys so if the RSI goes below the parameters set by the user the bot will trade again as if none of the buys were triggered. This was done to improve W/R and ROI of the strategy after a lot of testing. The reason for this is because we had our first win when we hit the first TP and have a chance of accumulate again if price retests those RSI levels.
Lets take a look at another example, where the bot goes full position and sell the whole position:

![image](https://github.com/asier13/Python-Trading-Bot/assets/62717613/e04aa5cd-e19d-4142-a261-fb92fea3bb41)

This is because the RSI closed below 26 and all buy entries where triggered, same with the TPs where the first one was when it closed with a 1% profit and second one because the RSI of the previous candle (marked with the second green line) above 65. If the bot didnt close, we would have touched the SL.
This is the reason why we use the RSI in the buys and with the TPs, to secure profits and not depend on percentages. Here is the code for the TPs section:

<img width="512" alt="image" src="https://github.com/asier13/Python-Trading-Bot/assets/62717613/14d6f9c6-5d61-4f5c-8c98-f7125f50b7c1">

The buys are set at those RSI values for a reason, the bounces that we are looking for in this strategy are more likely in that 29-26 RSI value zone, giving us more W/R and more ROI because we get a better entry.
Here is an example if we set the RSI values at 31 or 30 for example marked with circles that proof that we would have a lower W/R and higher drawdown:

![image](https://github.com/asier13/Python-Trading-Bot/assets/62717613/3e05dfed-d8a4-4423-90c5-243d9bdffd73)


Last example to explain how we would hold the position and understand how the SL works in this strategy.
So for the first scenario, sometimes the RSI value will go below 26 which is my last buy trade but we wouldnt get the bounce we want, but because we are trading on lower timeframes, we would have to wait for the higher timeframes to do the work for us.
Here we would go full position as the RSI goes below 26 but we will only get a 0.55% bounce and RSI doesnt even reach 45, which is not enough to trigger our TPs. Price keeps falling and the bot just waits for TPs or the SL. 

![image](https://github.com/asier13/Python-Trading-Bot/assets/62717613/3603eb2b-5028-442f-8ebe-f6a1412f8ed6)


The lowest it gets is -1.28%, which is far from our SL in -2% and the bot keeps waiting. But the bounce comes and the RSI values trigger the RSI TPs, first at 55 and later on, at 65. These TPs in this situation act as SL because the PNL when the RSI is at 55 is at -0.25% and when it gets to 65 its basically B/E.
For cases with strong downtrend and no bounces its very important to have a SL to avoid losing our capital, so here is an example, where price is falling heavy and we go full position, but the SL gets triggered as we fall below our -2% SL:

![image](https://github.com/asier13/Python-Trading-Bot/assets/62717613/8335ad1b-3174-4f95-91e0-ce0e94d1e011)


Because we are full position, the bot cant keep adding trades, so it has to wait for the price to bounce or the SL. When we touch the SL we sell the position at a -2% loss, the percentage depends on the asset and risk management of the user as I said at the beginning.
The bot as soon as it sells, it triggers a buy and goes full position again because the previous candle closed with a RSI value below 26. After that it waits for new trades, either the TPs or SL to get triggered, in that case it was the TPs:

![image](https://github.com/asier13/Python-Trading-Bot/assets/62717613/a04894d8-24f1-4a14-a53b-3c9bc5313a0b)

If the price continued dropping, the bot will wait for next buying opportunities.

When the analysis is finished, the bot stores the best assets with a ROI over 50% and a W/R over 70%, saving the values of the parameters used, the date the user used to analyze the PA of the asset using the strategy, the initial bank, roi, W/R and drawdown.

I hope you appreciate the work and the analysis. This is NFA and DYOR as always. Have fun with it!



