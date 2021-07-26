WPATH="/tmp"
DAY=$(date +%Y-%m-%d)

if [ -z $1 ]; then
	echo "Usage: import_manually_sells $DAY"
	exit 1
fi

DAY=$1


file_nef=/home/dp/nef/data/sells/$DAY.log
file_lpf=/tmp/nef_manually.lpf

echo $file_nef

#echo Converting CSV to Line Protocol: $file_csv  ==> $file_lpf
python3 /home/dp/nef/influx_nefsells.py $file_nef > $file_lpf

#echo Import into database: $file_lpf
bash /home/dp/nef/import_to_influx.sh $file_lpf
