################################################################################
#
# Framework for testing sub routines of the TG bot.
#
# The bot doesn't stop on Python errors. Calling the routines with exmple data
# is sometimes helpfule. The routines have to to be copied over from the bot's
# code into this program and made changes have to be be merged into the code
# manually.
#
################################################################################

#
########## Imports  and globals used by the bot
#
import base64
import re

m_symbol = ""
m_priceB = 0.0
m_priceS = 0.0
m_qty = 0.0



#
########## Test data
#
line0 = '2021/08/06 01:32:30 [FILLED] {"symbol":"ICPEUR","orderId":5148711,"clientOrderId":"x-J6MCRYME-35-9417601719804103665023","price":"36.40000000","origQty":"2.77000000","executedQty":"2.77000000","cummulativeQuoteQty":"100.82800000","status":"FILLED","timeInForce":"GTC","type":"LIMIT","side":"SELL","stopPrice":"0.00000000","icebergQty":"0.00000000","time":1627860722620,"updateTime":1628206088056,"isWorking":true,"isIsolated":false}'
line1 = '2021/08/06 11:15:09 [FILLED] {"symbol":"FISUSDT","orderId":16435188,"clientOrderId":"91eyJwIjozLjQxOCwibSI6MS4wN30","price":"3.65700000","origQty":"29.53300000","executedQty":"29.53300000","cummulativeQuoteQty":"108.00218100","status":"FILLED","timeInForce":"GTC","type":"LIMIT","side":"SELL","stopPrice":"0.00000000","icebergQty":"0.00000000","time":1619987544330,"updateTime":1628241043904,"isWorking":true,"isIsolated":false}'
line2 = '2021/07/31 02:27:25 [FILLED] {"symbol":"QTUMUSDT","orderId":568365111,"clientOrderId":"01eyJwIjo3LjEzNywibSI6MS4wNX0","price":"7.49400000","origQty":"7.00700000","executedQty":"7.00700000","cummulativeQuoteQty":"52.51045800","status":"FILLED","timeInForce":"GTC","type":"LIMIT","side":"SELL","stopPrice":"0.00000000","icebergQty":"0.00000000","time":1625599500575,"updateTime":1627690682133,"isWorking":true,"isIsolated":false}'



# \  / \  / \  / \  / \  /          \  / \  / \  / \  / \  /
#  \/   \/   \/   \/   \/  Bot Code  \/   \/   \/   \/   \/ 

########################################
# Sub:
#
#   Extracts old JSON metadata from clientOrderId
########################################
def extractMetadata( clientOrderId):
    global m_priceB
    pattern = '.*"p":([0-9\.]+),.*"m":([0-9\.]+)}'

    data = clientOrderId[2:]

    # add maximum padding. Excess chars are ignored. No fancy length calculation needed.
    data = data + "===="
    json = base64.b64decode(data)
    print (json)

    # Extract metadata if found
    match = re.match(pattern, json)
    if ( match is not None):
        m_priceB = match.group(1)
        return True
    else:
        return False



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

    # What info is in the line?
    match_old = re.search( pattern_old, line)
    match_168 = re.search( pattern_168, line)
    match_non = re.search( pattern_non, line)

    # Line contains "bought at:"
    if ( match_old is not None):
        m = match_old
        m_symbol = m.group(1)
        m_priceS = float(m.group(2)) 
        m_qty = float(m.group(3))
        m_priceB = float(m.group(4))

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

        # preset value
        m_priceB = m_priceS * mult

        m2 = re.match( pattern_cid, line)

        if ( m2 is not None):
            if ( extractMetadata(m2.group(1))):
                print( "Found price in Metadata: " + str(m_priceB))
            else:
                print( "DEBUG: " + line)
        else:
            print( "DEBUG: match empty! " + line)
    else:
        print( "Failure")


# -/\--/\--/\--/\--/\- Bot Code -/\--/\--/\--/\--/\-
#--------------------------------------------------- 


#####
# Test subs
#####

print( "---------- test line0")
extractFromLine( line0)
print( "bought at: " + str(m_priceB))
print( "---------- done line0\n")


print( "---------- test line1")
extractFromLine( line1)
print( "bought at: " + str(m_priceB))
print( "---------- done line1\n")


print( "---------- test line2")
extractFromLine( line2)
print( "bought at: " + str(m_priceB))
print( "---------- done line2\n")




######################################
print( "---------- test decoding...")
pattern = '.*"p":([0-9\.]+),.*"m":([0-9\.]+)}'
exdata = "91eyJwIjozLjQxOCwibSI6MS4wN30"
exdata = "01eyJwIjo3LjEzNywibSI6MS4wNX0"
data = exdata[2:]
print ( "Data: "  + data)

# add maximum padding. Excess chars are ignored. No fancy length calculation needed.
data = data + "===="
print( "Extended: " + data)
json = base64.b64decode(data)
print (json)


match = re.match(pattern, json)
print(match.group(1))
print(match.group(2))
print( "---------- done decoding\n")

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nowrap
