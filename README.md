# *DISCLAIMER*
I only use these tools for **Binance**
Incase the log data from other echanges differs from the binance logs, there might be a lot more work to do and all my stuff merely works as an idea or framework for you.

# nef_tools
Tools to handle logs of Nefertiti

Here is a collection of tools I use to get infos from the Nefertiti logs (https://github.com/svanas/nefertiti)
They are (currently) just for my needs. You most likely need to adjust paths and other stuff to use them.
A detailed documentation will follow - eventually :-)

# The Idea
The **sell bot** (*cryptotrader* started with comand *sell*) logs, among other things, all filled buy and sell trades. These log entries contain all the infos needed (more on that later) to calculated the exact difference of a specific buy-sell trade combo (called **gain** from now on).
To get a good approximation of the money earned withteh bot I started to store my logs and get the info from them. It is a just an estimation, because sometimes (very rarely) log enties get lost. For example I suspect problems writing to the logfile when I investigate it manually. To be a bit safer I write two logfiles and only use one for manual inspection. Additionally, I extract the daily infos into daily files (which additionally get archived) so I should have at lest those.

# The Data
The format of the logged data has changed a few times. The worst changes was around version 0.0.158 without notification.
Some of my curent date is a bit messed up, because the log format was changed (around version 0.0.158?) without any notification. Before that 


### Here is an entry from an older version:
```JSON
2021/05/12 16:27:54 [FILLED] {"symbol":"ETHEUR","orderId":4492XXXXX,"orderListId":-1,"clientOrderId":"31eyJwIjozNTAwLCJtIjoxLjAzfQ","price":"3605.00000000","origQty":"0.XXXXX000","executedQty":"0.XXXXX00","status":"FILLED","timeInForce":"GTC","type":"LIMIT","side":"SELL","stopPrice":"0.00000000","icebergQty":"0.00000000","time":1620808021217,"metadata":"bought at: 3500.00000000, mult: 1.03"}
```

Info found here: sell price (3605.00), quantity, buy price (3500.00).
The *metadata* is cleverly encoded in the *clientOrderId*

### Example of entry before 0.0.168
```JSON
2021/07/12 01:49:11 [FILLED] {"symbol":"AXSUSDT","orderId":2974XXXXX,"clientOrderId":"x-J6MCRYME-8719671563043378493719905","price":"19.00000000","origQty":"X.XX000000","executedQty":"X.XX000000","cummulativeQuoteQty":"XX.XXX00000","status":"FILLED","timeInForce":"GTC","type":"LIMIT","side":"SELL","stopPrice":"0.00000000","icebergQty":"0.00000000","time":1625928380738,"updateTime":1626046701192,"isWorking":true,"isIsolated":false}
```

There is **no enough** information availale. the info regarding the buy order is missing.

### Example of entry after 0.0.168
```JSON
2021/07/31 01:51:40 [FILLED] {"symbol":"BTCEUR","orderId":979689971,"clientOrderId":"x-J6MCRYME-34000-0369125507988434722","price":"35360.00000000","origQty":"0.0XXXXX00","executedQty":"0.0XXXXX00","cummulativeQuoteQty":"XX.XXX32000","status":"FILLED","timeInForce":"GTC","type":"LIMIT","side":"SELL","stopPrice":"0.00000000","icebergQty":"0.00000000","time":1627453433490,"updateTime":1627688696953,"isWorking":true,"isIsolated":false}
```

Here the *clientOrderId* contains the buy price (34000) again.

# The tools
## save the sell logs
This is for calling it via Bash. The *Powershell* version (found in the Telegram group) will be added soon.
```Bash
cryptotrader sell [YOUR PARAMETERS] 2>&1 | tee -a sell_binance.log out_sell_binance.log | grep FILLED >> filled_binance.log
```
Writing it to two files is to be safe to inspect it while the bot is running. And the *filled.log* is for convenience ATm as this is the info I am most interested in.

## extract the daily entries
The file `dailysells.sh` does the extraction of filled sell orders for the day. it should be run via *cron* like so:
```crontab
*/5 * * * * /bin/sh /home/dp/crypto/dailysells.sh
```
It uses `clean_sells.sh` to remove unwanted lines.
The resulting info is written to a file in *sells/YYYY-MM-DD.log*. These files are used later on!
**The folder names needs to be adjusted to your local filesystem**

## The Telegram Bot
The file `tg_gains_bot.py` contains the code for the Telegram bot.
It uses Python 2.7 (adjustmens for Python 3 might be neeed). The basics on how to write the bot was found on the Internet and used by me years ago for another purpose. So there might be code in it which is from the former usage. I hope i have removed most of it.
It needs to access the daily sell files created above. So either run it on the same computer (reachable via the Internet) or sync the files to the computer where the bot is running.
The bot reads the data from the files and calculates the gains and adds them to the output string.
All three log entry types should be supported (somewhat). Because for a few versions there was no info in the entries a fixed "mult" value is used set to 3% in my case, needs adjustment if youused another.
```Python
def getGainsFromFile( fname, detailed=True, onlyQuotes="EUR"):
    msg = ""
    mult = 0.03
```
The following commands are implemented so far:
* 'gains'
* 'gainsUSDT'
* 'gainsd'
* 'avgd'

### gains
Lists the gains of the last seven days. Can be configured in code:
```Python
    # Print latest 7 in list
    for fname in files[-7:]:
        msg = fname + ": "
        msg += getGainsFromFile( fpath+fname, detailed=False, onlyQuotes="EUR")
```
If detailed is TRUE it lists all gains for all seven days. If FALSE it list only the sum for each day. After the sums of the last days it adds the detailed list of gains from today.
The parameter *onlyQuotes* should be set to make the sum meaningful. In that case only the pairs with the given ending will be used.
for example "BTCEUR", ETHEUR" and "DOGEEUR" but not "BTCUSDT" or "AVAXBTC".

### gainsd
Lists only the (detailed) gains for today in the hard-coded quote

### gainsUSDT
Similar to **gains** but with *USDT* as quote currency.

### avgd
Calculates the daily average for a hard-coded quote currency (EUR).


### Note
It was planed to add commands for monthly stuff as well. Therefore the *archive* is constructed via `archive_sells.sh`. But this is not done yet.


## InfluxDB and Grafana (*WIP*)
The files
* import_manually_sells.sh
* import_todays_sells.sh
* influx_import.sh
* influx_nefsells.py

Are used to add the data into an InfluxDB. This database can then be used via *Grafana* to have a nice overview of your gains.


## Other shell tools
The script `listbots.sh` simply displays either running *buy* or *sell* bots using the *ps* and removes some fileds of the output. This assumes all bots are started more or less with the same order of parameters :)



