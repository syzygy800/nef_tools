from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import re
import os


##
##
##
output = ''
item = False



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
        '/gains /gainsUSDT /gainsd /avgd'
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


#######################################
#
# Command: gains
#
#######################################


########################################
# Sub: Truncate to 2 decimals
########################################
def trunc2( val):
    return int(val*100) / 100.0
    


########################################
# Sub: Create gains string for on file
#   Uses a fixed percentage (aka --mult)
########################################
def getGainsFromFile( fname, detailed=True, onlyQuotes="EUR"):
    pattern_old = 'symbol":"([A-Z]+)".*price":"([0-9.]+)",.*executedQty":"([0-9.]+)".*at: ([0-9.]+)'
    pattern = 'symbol":"([A-Z]+)".*price":"([0-9.]+)",.*executedQty":"([0-9.]+)"'
    m_symbol = ""
    m_priceS = 0.0
    m_qty = 0.0
    total = 0.0
    lines = []
    msg = ""
    mult = 0.03

    with open( fname) as f:
        lines = f.readlines()
    
    for l in lines:
        out = ""

        if ( "bought at" not in l):

            m = re.search( pattern, l)
            m_symbol = m.group(1)

            # Only sum wanted quotes
            quoteLen = len(onlyQuotes)
            if ( m_symbol[-quoteLen:] != onlyQuotes):
                continue
    
            m_priceS = float(m.group(2)) 
            m_qty = float(m.group(3))
            tots = m_priceS*m_qty
            g = tots * mult
            total += g
        else:
            m = re.search( pattern_old, l)

            m_symbol = m.group(1)

            # Only sum wanted quotes
            quoteLen = len(onlyQuotes)
            if ( m_symbol[-quoteLen:] != onlyQuotes):
                continue
    
            m_priceS = float(m.group(2)) 
            m_qty = float(m.group(3))
            m_priceB = float(m.group(4))
            tots = m_priceS*m_qty
            totb = m_priceB*m_qty
            g = (tots-totb)
            print g
            total += g



        out = l[11:16] + " " + m_symbol + ": <b>" + str( trunc2( g))

        if ( detailed):
            msg += out + "</b>\n"
    
    # output
    if ( detailed):
        msg += "<b>Total: " + str(trunc2(total)) + " " + onlyQuotes + "</b>"
    else:
        msg += "<b> " + str(trunc2(total)) + " " + onlyQuotes + "</b>"
    

    return msg
 


########################################
# Sub: Create gains string for on file
#   Uses the metadata info from older logfiles
########################################
def getGainsFromFile_old( fname, detailed=True, onlyQuotes="EUR"):
    pattern = 'symbol":"([A-Z]+)".*price":"([0-9.]+)",.*executedQty":"([0-9.]+)".*at: ([0-9.]+)'
    m_symbol = ""
    m_priceB = 0.0
    m_priceS = 0.0
    m_qty = 0.0
    total = 0.0
    lines = []
    msg = ""

    with open( fname) as f:
        lines = f.readlines()
    
    for l in lines:
        out = ""
        m = re.search( pattern, l)

        m_symbol = m.group(1)

        # Only sum wanted quotes
        quoteLen = len(onlyQuotes)
        if ( m_symbol[-quoteLen:] != onlyQuotes):
            continue
    
        m_priceS = float(m.group(2)) 
        m_qty = float(m.group(3))
        m_priceB = float(m.group(4))
        tots = m_priceS*m_qty
        totb = m_priceB*m_qty
        g = (tots-totb)
        total += g

        out = l[11:16] + " " + m_symbol + ": <b>" + str( trunc2( g))

        if ( detailed):
            msg += out + "</b>\n"
    
    # output
    if ( detailed):
        msg += "<b>Total: " + str(trunc2(total)) + " " + onlyQuotes + "</b>"
    else:
        msg += "<b> " + str(trunc2(total)) + " " + onlyQuotes + "</b>"
    

    return msg
    

########################################
# Main: Called by handler "gains"
########################################
def gains(bot, update):
    lines = []
    fpath = "/home/dp/crypto/sells/"
    fname = "2021-03-05.log"


    files = os.listdir("/home/dp/crypto/sells")
    files.sort(reverse=False)
    current = files.pop(-1)


    # Print latest 7 in list
    for fname in files[-7:]:
        msg = fname + ": "
        msg += getGainsFromFile( fpath+fname, detailed=False, onlyQuotes="EUR")
        bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode="HTML")

    # Latest file (current day)
    msg = '<u>' + current + "</u>\n"
    msg += getGainsFromFile( fpath+current, detailed=True, onlyQuotes="EUR")
    bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode="HTML")

    # Print shortcuts
    shorts( bot, update)
    

########################################
# Command: "gainsUSDT"
########################################
def gainsUSDT(bot, update):
    lines = []
    fpath = "/home/dp/crypto/sells/"
    fname = "2021-03-05.log"


    files = os.listdir("/home/dp/crypto/sells")
    files.sort(reverse=False)
    current = files.pop(-1)

    for fname in files[-10:]:
        msg = fname + ": "
        msg += getGainsFromFile( fpath+fname, detailed=False, onlyQuotes="USDT")
        bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode="HTML")

    # Latest file (current day)
    msg = '<u>' + current + "</u>\n"
    msg += getGainsFromFile( fpath+current, detailed=True, onlyQuotes="USDT")
    bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode="HTML")

    # Print shortcuts
    shorts( bot, update)



########################################
# Main: Called by handler "gainsd"
########################################
def gainsd(bot, update):
    lines = []
    fpath = "/home/dp/crypto/sells/"
    fname = "2021-03-05.log"


    files = os.listdir("/home/dp/crypto/sells")
    files.sort(reverse=False)
    current = files.pop(-1)

    # Latest file (current day)
    msg = '<u>' + current + "</u>\n"
    msg += getGainsFromFile( fpath+current, detailed=True, onlyQuotes="EUR")
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

    files = os.listdir("/home/dp/crypto/sells")
    files.sort(reverse=False)

    for fname in files:
        msg = getGainsFromFile( fpath+fname, detailed=False)
        entries = msg.split(" ")
        total += float(entries[1])
        count += 1

    msg = "Daily average: " + str(trunc2(total/count)) + " EUR"
    bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode="HTML")

    # Print shortcuts
    shorts( bot, update)



#######################################
#
#
#
#######################################
def clear_globals():
    global output
    global done

    done = False
    output = ''



#######################################
#
#
#
#######################################
# Add your Telegram bot token here
updater = Updater('XXXXXXXXX:XXXXXXXXXXXXXXXX-XXXXXXXXXXXXXXXXXX')

updater.dispatcher.add_handler(CommandHandler('start',      start))
updater.dispatcher.add_handler(CommandHandler('hello',      hello))
updater.dispatcher.add_handler(CommandHandler('help',       help))
updater.dispatcher.add_handler(CommandHandler('gains',      gains))
updater.dispatcher.add_handler(CommandHandler('gainsUSDT',  gainsUSDT))
updater.dispatcher.add_handler(CommandHandler('gainsd',     gainsd))
updater.dispatcher.add_handler(CommandHandler('avgd',       avgd))

updater.start_polling()
updater.idle()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
