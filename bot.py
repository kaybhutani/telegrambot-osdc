import telebot
import time
import datetime
from pymongo import MongoClient
import config
from profanity import profanity

try:
	client = MongoClient(config.MONGODB_URI, connectTimeoutMS=30000)


except:
	print(e)


bot = telebot.TeleBot(token=config.bot_token)

admins=['kartikaybhutani', 'homuncculus', 'ryzokuken','dark_harryM']
def getRECORD(dbname):
    records = dbname.find({})
    return records

def pushRECORD(dbname, record):
    dbname.insert_one(record)

def getone(dbname, userid):
    data = dbname.find_one({"userid":userid})
    return data

def updateRecord(dbname, rec, update):
    dbname.update_one({'userid': rec['userid']},{
                              '$set': update
                              }, upsert=False)

@bot.message_handler(commands=['start']) # welcome message handler
def send_welcome(message):
    bot.reply_to(message, 'Welcome! Use /addevent to Add an upcoming event and use /top10 to add an article link.\n Use /upcoming to View upcoming meetups.\n Use /top10 to view top10 articles.')

@bot.message_handler(commands=['help']) # help message handler
def send_welcome(message):
    bot.reply_to(message, 'This bot is for only OSDC admins.\nUse /addevent to Add an upcoming event and use /top10 to add an article link.')

@bot.message_handler(commands=['addevent']) # welcome message handler
def send_welcome(message):
    bot.reply_to(message,'Please send the event details in following format.\n\naddevent\nEvent title\nEvent date(dd/mm/yyyy)\nEvent time\nVenue')

@bot.message_handler(commands=['addarticle']) # welcome message handler
def send_welcome(message):
    bot.reply_to(message,'Please send article details in following format\naddarticle\nArticle title\nURL')


@bot.message_handler(func=lambda msg: msg.text is not None and 'addevent' in msg.text.lower())
def at_converter(message):
	if message.from_user.username in admins:
		try:
			texts = message.text.split('\n')
			title=texts[1]
			date=texts[2]
			time=texts[3]
			venue=texts[4]
			username=message.from_user.username
			db = client.get_database("jiitosdc")
			meetings=db.meetings
			rec = {
			'username':username,
			'title': title,
			"date": date,
			"time": time,
			"venue": venue,
			}
			pushRECORD(meetings, rec)
			bot.reply_to(message, 'Added event details succesfully! Use /upcoming to view upcoming events!')




		except Exception as e:
			bot.reply_to(message, 'Some error occured. Report to @kartikaybhutani')
			print(e)
	else:
		bot.reply_to(message, 'Sorry, You don\'t have admin rights')


@bot.message_handler(commands=['upcoming']) # welcome message handler
def send_welcome(message):
	db = client.get_database("jiitosdc")
	meetings=db.meetings
	events=getRECORD(meetings)
	temp=[]
	for document in events:
          temp.append(document)
	upcoming=[]
	for i in range (0,len(temp)):
	    date=temp[i]['date']
	    format_str = '%d/%m/%Y' # The format
	    datetime_obj = datetime.datetime.strptime(date, format_str)

	    if(datetime_obj > datetime.datetime.now()):
	        upcoming.append(temp[i])
	msg=''
	for i in range(0,len(upcoming)):
		msg=msg+'{}\n{}\n{}\n{}\n\n'.format(upcoming[-(i-1)]['title'],upcoming[-(i-1)]['date'],upcoming[-(i-1)]['time'],upcoming[-(i-1)]['venue'])
	bot.reply_to(message,msg)





@bot.message_handler(func=lambda msg: msg.text is not None and 'addarticle' in msg.text.lower())
def at_converter(message):
	if message.from_user.username in admins:
		try:
			texts = message.text.split('\n')
			title=texts[1]
			url=texts[2]
			username=message.from_user.username
			db = client.get_database("jiitosdc")
			top10=db.top10
			rec = {
			'username':username,
			'title': title,
			"url": url,
			}
			pushRECORD(top10, rec)
			bot.reply_to(message, 'Added Article details succesfully! Use /top10 to view articles')


		except Exception as e:
			bot.reply_to(message, 'Some error occured. Report to @kartikaybhutani')
			print(e)
	else:
		bot.reply_to(message, 'Sorry, You don\'t have admin rights')

@bot.message_handler(commands=['top10']) # welcome message handler
def send_welcome(message):
	db = client.get_database("jiitosdc")
	top10=db.top10
	articles=getRECORD(top10)
	temp=[]
	for document in articles:
	      temp.append(document)
	try:
		temp=temp[:10]
	except Exception as e:
		temp=temp
	
	# upcoming=[]
	# for i in range (0,len(temp)):
	#     date=temp[i]['date']
	#     format_str = '%d/%m/%Y' # The format
	#     datetime_obj = datetime.datetime.strptime(date, format_str)

	#     if(datetime_obj > datetime.datetime.now()):
	#         upcoming.append(temp[i])
	msg=''
	for i in range(0,len(temp)):
		msg=msg+'{}\n{}\n\n'.format(temp[-(i-1)]['title'], temp[-(i-1)]['url'])
	bot.reply_to(message,msg)



@bot.message_handler(func=lambda msg: msg.text is not None and '#spam' in msg.text.lower())
def at_converter(message):
	if message.from_user.username in admins:
		try:
			userid=message.reply_to_message.from_user.id
			db = client.get_database("jiitosdc")
			spams=db.spams
			data=getone(spams, userid)
			if data==None:
				rec={
				"userid":userid,
				"count":1
				}
				pushRECORD(spams, rec)
				bot.send_message(message.chat.id, 'Warned @{}, Warning count = 1'.format(message.reply_to_message.from_user.username))

			elif data['count']>=5:
				try:
					bot.send_message(message.chat.id, 'You have reached max limit of warnings! Removing you for now.\nMessage admins if you think this was a mistake.')
					bot.kick_chat_member(message.chat.id,data['userid'])
				except:
					bot.reply_to(message, 'Some Error occured, User might be admin.')
			elif data!=None and data['count']<5:
				rec=data
				rec['count']+=1
				updateRecord(spams, data, rec)
				bot.send_message(message.chat.id , 'Warned @{}, Warning count = {}'.format(message.reply_to_message.from_user.username, data['count']))				
			try:
				bot.delete_message(message.chat.id, message.reply_to_message.message_id)
			except:
				None
		except Exception as e:
			bot.reply_to(message, 'Some error occured. Report to @kartikaybhutani ?')
			print(e)
	else:
		bot.reply_to(message, 'Sorry, You don\'t have admin rights')

@bot.message_handler(func=lambda msg: profanity.contains_profanity(msg.text) )
def at_converter(message):
	bot.reply_to(message, "{}\n Please mind your language.".format(profanity.censor(message.text)))

bot.polling(none_stop=True)

# while True:
#     try:
#         bot.polling(none_stop=True)
#         # ConnectionError and ReadTimeout because of possible timout of the requests library
#         # maybe there are others, therefore Exception
#     except Exception:
#         time.sleep(15)