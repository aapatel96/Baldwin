from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Job, JobQueue
import telegram.replykeyboardmarkup
import telegram.keyboardbutton
import telegram

bot = telegram.Bot(token='297497718:AAFEZdRe7tbkt6z2Brb4tepPPCn5uNkrLlA')

updates = bot.getUpdates()
print updates
