import sys
import datetime
import pycurl
import io
import os
import re


#import requests



DATAFILE = "data/sells/2021-07-24.log"






##
##
##
def calcTimestamp(d, t, extra):
    stamp = 0
    
    parts = d.split("/")

    try:
        date = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
    except:
        print ("Failed date: " + d)

    parts = t.split(":")
    parts_s = parts[2].split(".")
    time = datetime.time(int(parts[0]), int(parts[1]), int(parts[2]), 1000*extra)


    dt = datetime.datetime(date.year, date.month, date.day, time.hour, time.minute, time.second, time.microsecond)
    stamp = 1000 * dt.timestamp()

    return (str(stamp))



########################################
# Sub: Create gains string for on file
#   Uses a fixed multiplier (aka --mult)
########################################
def getGainsFromFile( fname, detailed=True):
    pattern = 'symbol":"([A-Z]+)".*price":"([0-9.]+)",.*executedQty":"([0-9.]+)".*time":([0-9]+)'

    m_symbol = ""
    m_priceS = 0.0
    m_qty = 0.0
    total = 0.0
    lines = []
    outlines = []
    msg = ""
    mult = 0.03

    with open( fname) as f:
        lines = f.readlines()
    
    offset = 99
    for l in lines:

        # extract date and time the easy way
        parts = l.split(" ")
        timestamp = calcTimestamp( parts[0], parts[1], offset)
        offset += 0

        out = ""
        m = re.search( pattern, l)

        m_symbol = m.group(1)
        m_priceS = float(m.group(2)) 
        m_qty = float(m.group(3))
        m_time = m.group(4)

        tots = m_priceS*m_qty
        gain = tots * mult
        total += gain

        out = m_symbol + "," + str(timestamp).split(".")[0] + "," + str(gain)
        outlines.append(out)

    return outlines



########################################
# Sub: Create gains string for on file
#   Uses the metadata from older logfiles (pre version ???)
########################################
def getGainsFromFile_old( fname, detailed=True):
    pattern = 'symbol":"([A-Z]+)".*price":"([0-9.]+)",.*executedQty":"([0-9.]+)".*time":([0-9]+).*at: ([0-9.]+)'
    m_symbol = ""
    m_priceB = 0.0
    m_priceS = 0.0
    m_qty = 0.0
    total = 0.0
    lines = []
    outlines = []
    msg = ""

    with open( fname) as f:
        lines = f.readlines()
    
    offset = 99
    for l in lines:

        # extract date and time the easy way
        parts = l.split(" ")
        timestamp = calcTimestamp( parts[0], parts[1], offset)
        offset += 0

        out = ""
        m = re.search( pattern, l)

        m_symbol = m.group(1)
        m_priceS = float(m.group(2)) 
        m_qty = float(m.group(3))
        m_time = m.group(4)
        m_priceB = float(m.group(5))

        tots = m_priceS*m_qty
        totb = m_priceB*m_qty
        total += (tots-totb)


        out = m_symbol + "," + str(timestamp).split(".")[0] + "," + str(tots-totb)
        outlines.append(out)

    return outlines



##
##
##
def readDatalines(fname):
    datafile = open(fname, "r")
    lines = datafile.readlines()
    datafile.close()

    return (lines)



#####
#
# Main
#
#####
c = pycurl.Curl()

# Get filename from arguments
if ( len(sys.argv) > 1):
    DATAFILE = sys.argv[1]



# Create CSV lines of specified file
lines = getGainsFromFile( DATAFILE, detailed=True)

# Import line into Influx DB
for line in lines:
    values = line.split(",")
    d_symbol = values[0]
    d_timestamp = values[1]
    d_gain = values[2]

    # d_timestamp = str(calcTimestamp(d_day, d_time))

    result = u"sells"
    result += ",symbol=" + d_symbol
    result += " "
    result += "value=" + d_gain.rstrip().rstrip()
    result += " " + d_timestamp + "000000"

    c.setopt(c.URL, 'http://localhost:8086/write?db=nef_sells')
    c.setopt(c.POST, 1)
    c.setopt(c.WRITEDATA, io.StringIO(result))

    #c.perform()
    print (result)
    
c.close()

