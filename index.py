##import urllib
##import telegram
##import tweepy
##
##bot = telegram.Bot(token='297497718:AAFEZdRe7tbkt6z2Brb4tepPPCn5uNkrLlA')
##
##updates = bot.getUpdates()
##print updates

'''
Have to change the set function to new reading Function so that you give /newReading <dueDate> <reading>
and it splits the readings and starts sending messages
'''

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import time
from bs4 import BeautifulSoup
import urllib2
import requests
import PyPDF2
import nltk

segments = []
dueDates = []

class user:
    def __init__(self):
        self.segments = []

    
    

def split(string): 
    count = 0
    indexList=[]
    prevIndex = 0
    for i in range(len(string)):
        if string[i] == '.':
            count = count + 1
            ##print count
            if count%2 == 0:
                indexList.append(i)
                strInd = str(i)
                ##print "cut at "+ strInd
                
    for i in indexList:
        segments.append(string[prevIndex:i+1])
        prevIndex = i+1

    return segments
                   




# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)



# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hi!')


def help(bot, update):
    update.message.reply_text('Help!')

def splitMessage(bot, update):
    y = update.message.text.encode('utf-8')
    if y[0:4] == "http":
        webpage = urllib2.urlopen(y)
        html = webpage.read()
        soup = BeautifulSoup(html, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()

        text = soup.find_all('p')
        text = soup.get_text()

        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        split(text)
        update.message.reply_text("Webpage Read. Press n to flip through pages")
        return
    '''
    if update.message.text[len(update.message.text)-4:len(update.message.text)]==".txt":
        fileNameFinal = update.message.text
        fileObject = open(fileNameFinal, 'r')
        string = file.read()
        split(string)
        update.message.reply_text( "File read. Press n in telegram to flip")
        return
    '''
        
    if update.message.text == "n" or update.message.text == "N":
        if not segments:
            update.message.reply_text("Nothing to show")
            return
    
        update.message.reply_text(segments[0])
        segments.remove(segments[0])
        return
    

    else:      
        ##del segments[:]
        split(y)
        for i in segments:
            i.translate(None,"\n")
        update.message.reply_text("Message read. Press n to flip through pages")
           ## time.sleep(5)

def splitX(bot,update):
    PDF = update.message.document
    update.message.reply_text(PDF.mime_type)
    pdfFileObj = open(PDF, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    pageObj = pdfReader.getPage(0)
    update.message.reply_text(pageObj.extractText())


 
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("280514685:AAFHrtqjOaXPDhQZ6pFGYDD0N1mt6AcbqzY")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler([Filters.text], splitMessage))
    dp.add_handler(MessageHandler([Filters.document], splitX))

    

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
