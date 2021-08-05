#!/bin/bash


# Default file name for the log file
logfile=~/crypto/sell_binance_EUR.log


# Get the data from the command line and setup the variables
if [ -z $1 ]; then
        echo "Usage: bash dailysells_d.sh yyyy-mm-dd"
        exit 1
fi

date_file=$1
date_line=${date_file//-/\/}
tmp_file=/tmp/_tmp_$date_file.log


# Extract data from the logfile(s)
grep "$date_line.*\[FILLED\].*SELL" $logfile > $tmp_file

# if more logfiles are used add them like this (Note the ">>")
#grep "$date_line.*\[FILLED\].*SELL" $logfileX >> $tmp_file

# Remove identical orders
bash ~/crypto/clean_sells.sh $tmp_file | sort > ~/crypto/sells/$date_file.log
rm $tmp_file
