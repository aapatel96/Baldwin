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

from telegram.ext import Updater, CommandHandler, RegexHandler, MessageHandler, Filters, Job, JobQueue, ConversationHandler
import telegram.replykeyboardmarkup
import telegram.keyboardbutton
import logging
import time
from bs4 import BeautifulSoup
import urllib2
import requests
import PyPDF2
import requests
import shutil
import re
import os

#from pdf2text import Extractor


from HTMLParser import HTMLParser

CHOOSING,DUMMY = range(2)

flip_keyboard = telegram.replykeyboardmarkup.ReplyKeyboardMarkup([[telegram.KeyboardButton("next")]], resize_keyboard=True)
choosing_keyboard = telegram.replykeyboardmarkup.ReplyKeyboardMarkup([[telegram.KeyboardButton("summary")],[telegram.KeyboardButton("full")]], resize_keyboard=True)


users = []
segments = []
dueDates = []

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class user:
    def __init__(self,user_id):
        self.segments = []
        self.times = []
        self.user_id = user_id
        self.currentLink = ""
    def addSegments(self,list):
        for i in list:
            self.segments.append(i)
    def addTimes(self,list):
        for i in list:
            self.segments.append(i)

def start(bot, update):
    update.message.reply_text('Hi!')
    update.message.reply_text('Send me a link and I will')
    users.append(user(update.message.from_user.id))   
    
def help(bot, update):
    update.message.reply_text('Help!')


def find_user(users, user_id):
    """
    Returns the user object with given user_id

    Args:
         users:   The list of user instances to search through.
         user_id: The ID of the user to find.

    Returns:
            The 'user' object with user_id.
    """
    for i in range(len(users)):
        if users[i].user_id == user_id:
            return users[i]

    return None

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext   
    
def send_message_from_queue(bot, job):
    """
    Sends the next segment from segments used for jobs in a queue

    Args:
        bot: object of the current bot
        job: the job in which this is being added
        user_id: the user_id of the user to whom this will be sent

    """
    userfind = find_user(users, job.context)
    if userfind == None:
        update.message.reply_text("Please type /start and then resend url/text")
        return    
    bot.sendMessage(chat_id=job.context, text= userfind.segments[0],parse_mode="HTML", reply_markup=flip_keyboard)
    userfind.segments.remove(userfind.segments[0])
def send_message_from_button(bot,update):
    userfind = find_user(users, update.message.from_user.id)
    if userfind == None:
        update.message.reply_text("Please type /start and then resend url/text")
        return
    if not userfind.segments:
        update.message.reply_text("Nothing to show")
        return

    update.message.reply_text(userfind.segments[0],parse_mode="HTML",reply_markup=flip_keyboard)
    userfind.segments.remove(userfind.segments[0])
    return
def split_reading(reading, output): 
    """
    Splits a given reading into chunks of 2 sentences.

    Args:
         string: The string to chunkify.
         output: The list to store the chunks in.
                  Assumes len(output) == 0.
    Returns:
         output
    """
    sentences = reading.split(".")

    # Jump by 3 sentences and merge 3 sentences at a time.
    for i in xrange(0, len(sentences), 3):
        # If odd number of sentences and at last one,
        # keep in place.
        if len(sentences)%3 == 1:
            if i == len(sentences) - 1:
                output.append(sentences[i]) # ## # ## # ## # #
                return
        if len(sentences)%3 == 2:
            if i == len(sentences) - 2:
                output.append(sentences[i] + sentences[i+1])
                return

        # concat 2 sentences and save into array.
        output.append(sentences[i] + ". " + sentences[i+1] + "." + sentences[i+2] + ".")

    return output

# def send_message_from_keypress(bot,update):


def splitPDF(bot, update):
    file_id= update.message.document.file_id
    url = bot.getFile(file_id).file_path
    print url
    file = requests.get(url, stream=True)
    dump = file.raw
    print dump
    fileName = "file" + file_id+".pdf"
    with open(fileName, 'wb') as location:
        shutil.copyfileobj(dump, location)
    del dump
    pdfFileObj = open(fileName,"rb")
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    print pdfReader.numPages
    pageObj = pdfReader.getPage(0)
    print pageObj.extractText()
    
def askMode (bot,update):
    userfind = find_user(users,update.message.from_user.id)
    if userfind == None:
        update.message.reply_text("Please type /start and then resend url/text")
        return
    update.message.reply_text("do you want a summary or the full article?",reply_markup=choosing_keyboard)
    return CHOOSING

def full(bot,update):
    userfind = find_user(users,update.message.from_user.id)
    if userfind == None:
        update.message.reply_text("Please type /start and then resend url/text")
        return
    update.message.reply_text(userfind.segments[0],parse_mode="HTML", reply_markup=flip_keyboard)
    userfind.segments.remove(userfind.segments[0])
    return ConversationHandler.END


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

def process_message(bot, update, job_queue):
    userfind = find_user(users,update.message.from_user.id)
    if userfind == None:
        update.message.reply_text("Please type /start and then resend url/text")
        return
    message_text = update.message.text.encode('utf-8')
    if message_text[0:4] == "http":
        webpage = urllib2.urlopen(message_text)
        html = webpage.read()
        soup = BeautifulSoup(html, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        for match in soup.findAll('span'):
            match.unwrap()

        

#       text = soup.get_text()

##      invert comments between ##'s and switch #'s off for old way only with #'s at left most space
        text = soup.find_all('p')
        p_tags = []
        for i in text:
            p_tags.append(str(i))
                
        p_tags_pure = []
        for j in p_tags:
            if j[0:3] =="<p>":
                p_tags_pure.append(j)
        p_tags_double_pure = []
        for i in p_tags_pure:
            try:
                textToAppend = i[3:-4]
                p_tags_double_pure.append(textToAppend)

            except:
                pass

##            

        lines = (line.strip() for line in p_tags_double_pure)
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        print type(text)


        

        
##        split_reading(text, userfind.segments)


       
        for i in xrange(0,len(p_tags_double_pure),2):
            if (len(p_tags_double_pure))%2 == 1 and i == len(p_tags_double_pure)-1:
                segment = cleanhtml(p_tags_double_pure[i])
            else:
                segment = cleanhtml(p_tags_double_pure[i] +"\n"+"\n"+ p_tags_double_pure[i+1])

            userfind.segments.append(segment)
##
        update.message.reply_text("Webpage Read. Press n to flip through pages",reply_markup=flip_keyboard)

        for i in xrange(len(userfind.segments)):
            segment_alarm = Job(send_message_from_queue,
                                i*7*60,
                                repeat=False,
                                context=update.message.chat_id)

            job_queue.put(segment_alarm)
        return
    else:      
        ##del segments[:]
        userfind = find_user(users, update.message.from_user.id)
        if userfind == None:
            update.message.reply_text("Please type /start and then resend url/text")
            return
        split_reading(message_text, userfind.segments)
        ##for i in userfind.segments:
        ##i.translate(None,"\n")

        for i in userfind.segments:
            i.translate(None,"\n")
            segment_alarm = Job(send_message_from_queue,
                                i*30.0*60,
                                repeat=False,
                                context=update.message.chat_id)
            job_queue.put(segment_alarm)
        update.message.reply_text("Message read. Press n to flip through pages",reply_markup=flip_keyboard)
           ## time.sleep(5)
    '''
    if update.message.text[len(update.message.text)-4:len(update.message.text)]==".txt":
        fileNameFinal = update.message.text
        fileObject = open(fileNameFinal, 'r')
        string = file.read()
        split(string)
        update.message.reply_text( "File read. Press n in telegram to flip")
        return
    
        update.message.reply_text(userfind.segments[0])
        userfind.segments.remove(userfind.segments[0])
        return
    
    '''


def first_last(bot,update, args):
    message_text = args[0].encode('utf-8')
    webpage = urllib2.urlopen(message_text)
    html = webpage.read()
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()

    

#       text = soup.get_text()

##      invert comments between ##'s and switch #'s off for old way only with #'s at left most space
    text = soup.find_all('p')
    p_tags = []
    for i in text:
        p_tags.append(str(i))
    p_tags_pure = []
    for j in p_tags:
        if j[0:3] =="<p>":
            p_tags_pure.append(j)
    p_tags_double_pure = []
    for k in p_tags_pure:
        try:
            textToAppend = cleanhtml(k[3:-4])
            p_tags_double_pure.append(textToAppend)
        except:
            pass
    #print "removed <p>"
    summary= [p_tags_double_pure[0]]
    #print "created list to store the segments of the summary"
    end_index = len(p_tags_double_pure)-1
    #print "end index is calculated as all but the last one"
    for l in xrange(1,end_index):
        #print "looping over " + str(l) + " p_tag"
        para = p_tags_double_pure[l]
        #print "pulling element at index " + str(l) + " of p_tags"
        para_sentences = para.split('.')
        #print "splitting element by sentence"
        if len(para_sentences)==1:
            summary.append(para_sentences[0])
            continue
        #print "para has more than one sentence"
        summary.append(para_sentences[0])
        
        summary.append(para_sentences[-1])
        #print "appending first and last sentences of para"

    #print "out of loop"
    summary.append(p_tags_double_pure[-1])
    userfind = find_user(users, update.message.from_user.id)
    if userfind == None:
        update.message.reply_text("Please type /start and then resend command")
        return
    for i in summary:
        if len(i) <=3:
            continue
        userfind.segments.append(i)

    update.message.reply_text("Press /next to flip through- NO JOB QUEUE SET... this is a summary BC read it or die",reply_markup=flip_keyboard)
        
        
    
        
##            
    '''
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    '''
    
 
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    TOKEN = '280514685:AAFHrtqjOaXPDhQZ6pFGYDD0N1mt6AcbqzY'
    PORT = int(os.environ.get('PORT', '5000'))
    updater = Updater(TOKEN)
    # job_q= updater.job_queue

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(RegexHandler("^next$", send_message_from_button))
    dp.add_handler(MessageHandler(Filters.document, splitPDF))
    dp.add_handler(CommandHandler("firstlast",first_last, pass_args = True))

    

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, process_message, pass_job_queue=True))

    '''

    add_article = ConversationHandler(
    entry_points=[MessageHandler(Filters.text, askMode, pass_job_queue=True)],
    states={


        CHOOSING: [RegexHandler('^full$',passf),RegexHandler('^summary$',passf)],
        
        DUMMY: [RegexHandler('^cancel$', cancel),                        
                ],     
    },

    fallbacks=[RegexHandler('^cancel$', cancel)]
    )

    dp.add_handler(add_article)
    
    '''
    
    # log all errors
    dp.add_error_handler(error)
    
    updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
    updater.bot.set_webhook("https://baldwin-reader.herokuapp.com/" + TOKEN)
    # Start the Bot
##    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
