from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import re
import os
import sys
import base64


##
##
##
output = ''
item = False

m_symbol = ""
m_priceB = 0.0
m_priceS = 0.0
m_qty = 0.0
g_earn = []


#######################################
#
# Command: start
#
#######################################
def start(bot, update):
    hello(bot, update)
    help(bot, update)



#######################################
#
# Command: hello
#
#######################################
def hello(bot, update):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))



#######################################
#
# Command: shorts
#
#######################################
def shorts(bot, update):
    update.message.reply_text(
        '/eur_today /eur_7d /usdt_today /usdt_7d /btc_today /btc_7d /avgd'
    )



#######################################
#
# Command: help
#
#######################################
def help(bot, update):
    update.message.reply_text(
        'Commands:\n'
        '/help: this help\n'
        '/gains: show my  tendies\n'
        '/avgd: show daily average\n'
)



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
    json = base64.b64decode(data)

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
########################################
def getGainsFromFile( fname, detailed=True, onlyQuotes="EUR", earn=[], trunc=2):
    global m_symbol
    global m_priceB
    global m_priceS
    global m_qty

    total = 0.0
    lines = []
    msg = ""
    mult = 0.03
    formstr = "{:." + str(trunc) + "f}"


    with open( fname) as f:
        lines = f.readlines()

    for l in lines:
        out = ""

        # Set global variables, depending on line style
        extractFromLine( l)


        # Do not count symbols used in "--earn"
        if m_symbol in earn:
            continue

        # Only sum wanted quotes
        quoteLen = len(onlyQuotes)
        if ( m_symbol[-quoteLen:] != onlyQuotes):
            continue


        # Calc gains and total sum
        tots = m_priceS*m_qty
        totb = m_priceB*m_qty
        g = (tots-totb)
        total += g

        # Create output string
        out = l[11:16] + " " + m_symbol + ": <b>" + formstr.format( g)

        if ( detailed):
            msg += out + "</b>\n"

    # output
    if ( detailed):
        msg += "<b>Total: " + formstr.format( total) + " " + onlyQuotes + "</b>"
    else:
        msg += "<b> " + formstr.format( total) + " " + onlyQuotes + "</b>"


    return msg



########################################
# Command: "eur_7d"
########################################
def gainsEUR_7d(bot, update):
    lines = []
    fpath = "/home/dp/crypto/sells/"
    fname = "2021-03-05.log"


    files = os.listdir("/home/dp/crypto/sells")
    files.sort(reverse=False)
    current = files.pop(-1)


    # Print latest 7 in list
    for fname in files[-6:]:
        msg = fname + ": "
        msg += getGainsFromFile( fpath+fname, detailed=False, onlyQuotes="EUR", earn=g_earn)
        bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode="HTML")

    # Latest file (current day)
    msg = '<u>' + current + "</u>\n"
    msg += getGainsFromFile( fpath+current, detailed=True, onlyQuotes="EUR", earn=g_earn)
    bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode="HTML")

    # Print shortcuts
    shorts( bot, update)



########################################
# Command: "eur_today"
########################################
def gainsEUR_d(bot, update):
    lines = []
    fpath = "/home/dp/crypto/sells/"
    fname = "2021-08-17.log"


    files = os.listdir("/home/dp/crypto/sells")
    files.sort(reverse=False)
    current = files.pop(-1)

    # Latest file (current day)
    msg = '<u>' + current + "</u>\n"
    msg += getGainsFromFile( fpath+current, detailed=True, onlyQuotes="EUR", earn=g_earn)
    bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode="HTML")

    # Print shortcuts
    shorts( bot, update)



########################################
# Command: "usdt_7d"
########################################
def gainsUSDT(bot, update):
    lines = []
    fpath = "/home/dp/crypto/sells/"
    fname = "2021-03-05.log"


    files = os.listdir("/home/dp/crypto/sells")
    files.sort(reverse=False)
    current = files.pop(-1)

    for fname in files[-6:]:
        msg = fname + ": "
        msg += getGainsFromFile( fpath+fname, detailed=False, onlyQuotes="USDT", earn=g_earn)
        bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode="HTML")

    # Latest file (current day)
    msg = '<u>' + current + "</u>\n"
    msg += getGainsFromFile( fpath+current, detailed=True, onlyQuotes="USDT", earn=g_earn)
    bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode="HTML")

    # Print shortcuts
    shorts( bot, update)



########################################
# Command: "usdt_today"
########################################
def gainsUSDT_d(bot, update):
    lines = []
    fpath = "/home/dp/crypto/sells/"

    files = os.listdir("/home/dp/crypto/sells")
    files.sort(reverse=False)
    current = files.pop(-1)

    # Latest file (current day)
    msg = '<u>' + current + "</u>\n"
    msg += getGainsFromFile( fpath+current, detailed=True, onlyQuotes="USDT", earn=g_earn)
    bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode="HTML")

    # Print shortcuts
    shorts( bot, update)



########################################
# Command: "btc_7d"
########################################
def gainsBTC_7d(bot, update):
    lines = []
    fpath = "/home/dp/crypto/sells/"


    files = os.listdir("/home/dp/crypto/sells")
    files.sort(reverse=False)
    current = files.pop(-1)

    for fname in files[-6:]:
        msg = fname + ": "

    # Latest file (current day)
    msg = '<u>' + current + "</u>\n"
    msg += getGainsFromFile( fpath+current, detailed=True, onlyQuotes="BTC", trunc=6)
    bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode="HTML")

    # Print shortcuts
    shorts( bot, update)



########################################
# Command: "btc_today"
########################################
def gainsBTC_d(bot, update):
    lines = []
    fpath = "/home/dp/crypto/sells/"

    files = os.listdir("/home/dp/crypto/sells")
    files.sort(reverse=False)
    current = files.pop(-1)

    # Latest file (current day)
    msg = '<u>' + current + "</u>\n"
    msg += getGainsFromFile( fpath+current, detailed=True, onlyQuotes="BTC", earn=g_earn, trunc=6)
    bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode="HTML")

    # Print shortcuts
    shorts( bot, update)



#######################################
#
# Command: avgd
#
# Daily average over all data files
#
#######################################
def avgd(bot, update):
    lines = []
    fpath = "/home/dp/crypto/sells/"
    fname = ""
    count = 0
    total = 0
    count_usdt = 0
    total_usdt = 0

    files = os.listdir("/home/dp/crypto/sells")
    files.sort(reverse=False)

    for fname in files:
        msg = getGainsFromFile( fpath+fname, detailed=False)
        entries = msg.split(" ")
        total += float(entries[1])
        count += 1

        msg = getGainsFromFile( fpath+fname, detailed=False, onlyQuotes="USDT")
        entries = msg.split(" ")
        total_usdt += float(entries[1])
        count_usdt += 1

    msg = "<b>Daily averages:</b>\n"
    msg += "{:.2f} EUR\n".format( total/count)
    msg += "{:.2f} USDT\n".format( total_usdt/count_usdt)
    bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode="HTML")

    # Print shortcuts
    shorts( bot, update)



#######################################
#
#
#
#######################################
# Add your Telegram bot token here
tg_token = 'XXXXXXXXX:XXXXXXXXXXXXXXXX-XXXXXXXXXXXXXXXXXX'

# TG token can be set via the command line
if ( len(sys.argv) > 1):
    tg_token = str( sys.argv[1])

# Set global earn parameter here (TODO: from argv[])
g_earn = ["BNBEUR", "EURUSDT"]

updater = Updater( tg_token)
updater.dispatcher.add_handler(CommandHandler('start',      start))
updater.dispatcher.add_handler(CommandHandler('hello',      hello))
updater.dispatcher.add_handler(CommandHandler('help',       help))
updater.dispatcher.add_handler(CommandHandler('eur_today',  gainsEUR_d))
updater.dispatcher.add_handler(CommandHandler('eur_7d',     gainsEUR_7d))
updater.dispatcher.add_handler(CommandHandler('usdt_today', gainsUSDT_d))
updater.dispatcher.add_handler(CommandHandler('usdt_7d',    gainsUSDT))
updater.dispatcher.add_handler(CommandHandler('btc_today',  gainsBTC_d))
updater.dispatcher.add_handler(CommandHandler('btc_7d',     gainsBTC_7d))
updater.dispatcher.add_handler(CommandHandler('avgd',       avgd))

updater.start_polling()
updater.idle()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 nowrap
