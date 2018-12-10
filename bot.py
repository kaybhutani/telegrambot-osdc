import telebot
import time

bot_token='633214880:AAFT1IE1JJzPSZUSRBpOWHOQiOJmhC-kCZ0'

bot = telebot.TeleBot(token=bot_token)


@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.send_message(message.chat.id, 'Welcome!')

@bot.message_handler(commands=['add'])
def add(message):
	bot.send_message(message.chat.id,'Title?')




while True:
	try:
		bot.polling()
	except Exception as e:
		print(e)
		time.sleep(15)