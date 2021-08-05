#!/bin/bash
tmp_file=/tmp/_tmp_$(date +%Y-%m-%d).log


# old
# grep "$(date +%Y/%m/%d).*\[FILLED\].*metadata" ~/crypto/filled_binance_EUR.log > ~/crypto/sells/$(date +%Y-%m-%d).log

# Extract all lines containing filled sell orders. One per sell instance
grep "$(date +%Y/%m/%d).*\[FILLED\].*SELL" ~/crypto/sell_binance_EUR.log > $tmp_file
grep "$(date +%Y/%m/%d).*\[FILLED\].*SELL" ~/crypto/sell_binance_usdt.log >> $tmp_file
grep "$(date +%Y/%m/%d).*\[FILLED\].*SELL" ~/crypto/sell_binance_btc.log >> $tmp_file
grep "$(date +%Y/%m/%d).*\[FILLED\].*SELL" ~/crypto/sell_gdax.log >> $tmp_file

# Remove identical orders
bash ~/crypto/clean_sells.sh $tmp_file | sort > ~/crypto/sells/$(date +%Y-%m-%d).log
rm $tmp_file
