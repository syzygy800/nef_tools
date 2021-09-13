import sys
import datetime
import pycurl
import io
import os
import re
import base64


#import requests



DATAFILE = "data/sells/2021-07-24.log"



m_symbol = ""
m_priceB = 0.0
m_priceS = 0.0
m_qty = 0.0
g_earn = []



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
# Sub:
#
#   Extracts old JSON metadata from clientOrderId
########################################
def extractMetadata( clientOrderId):
    global m_priceB
    pattern = '.*"p":([0-9\.]+),.*"m":([0-9\.]+)}'

    # Cut off two leading digits
    data = clientOrderId[2:]

    # Maximum padding. Excess chars are ignored. No "len % 4" needed.
    data = data + "===="
    json = base64.b64decode(data).decode("utf-8")

    # Extract metadata if found.
    match = re.match(pattern, json)
    if ( match is not None):
        m_priceB = float(match.group(1))



########################################
# Sub:
#
#   Overwrites global variables
########################################
def extractFromLine( line):
    global m_symbol
    global m_priceB
    global m_priceS
    global m_qty

    mult = 1-0.03
    pattern_non = 'symbol":"([A-Z]+)".*price":"([0-9.]+)",.*executedQty":"([0-9.]+)"'
    pattern_old = 'symbol":"([A-Z]+)".*price":"([0-9.]+)",.*executedQty":"([0-9.]+)".*at: ([0-9.]+)'
    pattern_168 = 'symbol":"([A-Z]+)".*J6MCRYME\-([0-9_]+)\-.*price":"([0-9.]+)",.*executedQty":"([0-9.]+)"'
    pattern_cid = '.*"clientOrderId":"([a-zA-Z0-9=]+)"'
    pattern_market = 'symbol":"([A-Z]+)".*J6MCRYME\-([0-9_]+)\-.*executedQty":"([0-9.]+)".*cummulativeQuoteQty":"([0-9.]+)".*MARKET'

    # What info is in the line?
    match_old = re.search( pattern_old, line)
    match_168 = re.search( pattern_168, line)
    match_non = re.search( pattern_non, line)
    match_market = re.search( pattern_market, line)

    # Line contains "bought at:"
    if ( match_old is not None):
        m = match_old
        m_symbol = m.group(1)
        m_priceS = float(m.group(2)) 
        m_qty = float(m.group(3))
        m_priceB = float(m.group(4))

    # Line contains a MARKET order and "-PRICE-" in clientOrderid
    elif match_market is not None:
        m = match_market
        m_symbol = m.group(1)
        m_priceB = float(m.group(2).replace("_", "."))
        execQty = float(m.group(3))
        quoteQty = float(m.group(4))
        m_priceS = quoteQty / execQty
        m_qty = execQty

    # Line contains "-PRICE-" in clientOrderid
    elif match_168 is not None:
        m = match_168
        m_symbol = m.group(1)
        m_priceB = float(m.group(2).replace("_", "."))
        m_priceS = float(m.group(3)) 
        m_qty = float(m.group(4))

    # Line contains no info, using fixed value!
    elif match_non is not None:
        m = match_non
        m_symbol = m.group(1)
        m_priceS = float(m.group(2)) 
        m_qty = float(m.group(3))

        # preset value with fixed mulitplier
        m_priceB = m_priceS * mult

        # overwrite price if found (old clientorderid)
        match_cid = re.match( pattern_cid, line)
        if ( match_cid is not None):
            extractMetadata( match_cid.group(1))
    else:
        print( "Failure")



########################################
# Sub: Create gains string for on file
#   Uses a fixed multiplier (aka --mult)
########################################
def getGainsFromFile( fname, detailed=True, earn=[]):
    global m_symbol
    global m_priceB
    global m_priceS
    global m_qty

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

        # Set global variables, depending on line style
        extractFromLine( l)

        # Do not count symbols used in "--earn"
        if m_symbol in earn:
            continue

        tots = m_priceS*m_qty
        totb = m_priceB*m_qty
        gain = (tots - totb)

        out = m_symbol + "," + str(timestamp).split(".")[0] + "," + str(gain)
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
lines = getGainsFromFile( DATAFILE, detailed=True, earn=["BNBEUR"])

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

