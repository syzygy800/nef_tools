#!/bin/bash

FOLDER=/home/dp/crypto/sells
ARCHIVE=/home/dp/crypto/archive


for fname in $FOLDER/*; do
	f=$(basename -- "$fname")
	y=${f:0:4}
	m=${f:5:2}

	target=$ARCHIVE/$y/$m
	mkdir -p $target
	cp $fname $target
done
