OHLOG=/var/log/openhab2/events.log
WPATH="/tmp"
DAY=$(date +%Y-%m-%d)
TMPFILE="jee_"$DAY".log"

file_events=$OHLOG
file_csv=/tmp/jeedata_$DAY.csv
file_lpf=/tmp/jeedata_$DAY.lpf


#echo Importing from event file: $file_events
grep -a $DAY $file_events | grep -a "StateChangedEvent.*Jee" | sed  's/_/ /g' | awk '{print $1","$2","$5","$6","$11}' > $file_csv

#echo Converting CSV to Line Protocol: $file_csv  ==> $file_lpf
python3 /etc/openhab2/scripts/influx_home.py $file_csv > $file_lpf

#echo Import into database: $file_lpf
bash /etc/openhab2/scripts/import_jeedata.sh $file_lpf
