#!/bin/bash
sort -k4 $1 | uniq -f3
