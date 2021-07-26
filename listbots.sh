#!/bin/bash

# args:
#	buy/sell

if [ -z $1 ]
then
	side="[buy|sell]"
else
	side=$1
fi


FILTER_COLS="awk '{$4=$5=$6=$7=$8=""; print $0}'"


ps -eo args | grep cryptotrader | grep -v grep | awk '{$4=$5=$6=$7=$8=""; print $0}' | sort -k2  | grep $side 
