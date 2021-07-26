#!/bin/bash

if [ -z $1 ]; then
        echo "Usage: bash dailysells_d.sh yyyy-mm-dd"
        exit 1
fi

date_file=$1
date_line=${date_file//-/\/}
tmp_file=/tmp/_tmp_$date_file.log


grep "$date_line.*\[FILLED\].*SELL" ~/crypto/sell_binance_EUR.log > $tmp_file
grep "2021/07/09.*\[FILLED\].*SELL" ~/crypto/sell_binance_usdt.log >> $tmp_file
grep "2021/07/09.*\[FILLED\].*SELL" ~/crypto/sell_binance_btc.log >> $tmp_file
grep "2021/07/09.*\[FILLED\].*SELL" ~/crypto/sell_gdax.log >> $tmp_file

sh /home/dp/crypto/clean_sells.sh $tmp_file | sort > ~/crypto/sells/2021-07-09.log
rm $tmp_file
