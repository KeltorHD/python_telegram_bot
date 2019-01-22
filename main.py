# -*- coding: utf-8 -*-
import constants
import sqlite3
import time
from flask import Flask, request
import telebot
from flask_sslify import SSLify
import os

bot = telebot.TeleBot(constants.token, threaded=False)

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url="https://keltor.pythonanywhere.com")

app = Flask(__name__)
sslify = SSLify(app)

conn = sqlite3.connect("data.sqlite")
cursor = conn.cursor()

try:
	cursor.execute("CREATE TABLE users (chat_id integer, username text, pas text, user_table text, subs text, status text,day text, week text, name_write text, lesson text, l1 text, l2 text, l3 text, l4 text, l5 text, l6 text, l7 text, l8 text,t1 text,t2 text,t3 text,t4 text,t5 text,t6 text,t7 text,t8 text)")
except:
	pass

@app.route('/', methods=["POST"])
def webhook():
	bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
	return "ok", 200



### Commands
@bot.message_handler(commands=['start'])
def start(message):
	cursor.execute("SELECT chat_id FROM users WHERE chat_id = '{}'".format(message.chat.id))
	row = cursor.fetchone()
	if not row:
		cursor.execute("INSERT INTO users (chat_id, username) VALUES ('{}','{}')".format(message.chat.id, message.chat.username))
		conn.commit()
	cursor.execute("SELECT user_table FROM users WHERE chat_id = '{}'".format(message.chat.id))
	row = cursor.fetchone()[0]
	cursor.execute("UPDATE users SET status='' WHERE chat_id = '{}'".format(message.chat.id))
	conn.commit()
	if row:
		start_markup = telebot.types.ReplyKeyboardMarkup(True, False)
		start_markup.row('Расписание', 'Архив д/з')	
		start_markup.row('Просмотр дз на данную неделю', 'Просмотр дз на следующую неделю')
		start_markup.row('Заполнить дз на данную неделю', 'Заполнить дз на следующую неделю')
		bot.send_message(message.chat.id, 'Это главное меню, тыкни на кнопки внизу:', reply_markup=start_markup)
	else:
		bot.send_message(message.chat.id, 'Внеси собственное расписание (/new) или посмотри уже созданные (/connect). Помощь - /help')

@bot.message_handler(commands=['stop'])
def stop(message):
	try:
		cursor.execute("SELECT name_write FROM users WHERE chat_id = {}".format(message.chat.id))
		name_write = cursor.fetchone()[0]
		os.remove('/home/Keltor/table/{}.sqlite'.format(name_write))
	except:
		pass
	cursor.execute("UPDATE users SET user_table='',subs='',pas='',status='',day='',week='',name_write='',lesson='',l1='',l2='',l3='',l4='',l5='',l6='',l7='',l8='',t1='',t2='',t3='',t4='',t5='',t6='',t7='',t8='' WHERE chat_id = '{}'".format(message.chat.id))
	conn.commit()
	leave_markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(message.chat.id, 'Все остановлено. /start', reply_markup = leave_markup)

@bot.message_handler(commands=['new'])
def new(message):
	mes = bot.send_message(message.chat.id, 'Сколько дней ты учишься?(пять или шесть?). Ты можешь в любой момент закончить создание - /stop')
	bot.register_next_step_handler(mes, week_write)

def week_write(message):
	if message.text	== '/stop':
		stop(message)
		return None
	text = message.text.lower()
	if  text == '5' or text == 'пятидневка' or text == 'пять':
		cursor.execute("UPDATE users SET week = '{}' WHERE chat_id = '{}'".format(5, message.chat.id))
		conn.commit()
		mes = bot.send_message(message.chat.id, 'Отлично! Теперь, как ты назовешь свое расписание(его смогут видеть другие пользователи)?')
		bot.register_next_step_handler(mes, name_write)

	elif  text == '6' or text == 'шестидневка' or text == 'шесть':
		cursor.execute("UPDATE users SET week = '{}' WHERE chat_id = '{}'".format(6, message.chat.id))
		conn.commit()
		mes = bot.send_message(message.chat.id, 'Отлично! Теперь, как ты назовешь свое расписание(его смогут видеть другие пользователи)?')
		bot.register_next_step_handler(mes, name_write)

	else:
		mes = bot.send_message(message.chat.id, 'Не понял твое сообщение, напиши его по-другому')
		bot.register_next_step_handler(mes, week_write)

def name_write(message):
	if message.text	== '/stop':
		stop(message)
		return None
	cursor.execute("UPDATE users SET name_write = '{}' WHERE chat_id = '{}'".format(message.text, message.chat.id))
	conn.commit()
	pas_markup = telebot.types.ReplyKeyboardMarkup(True, False)
	pas_markup.row('/stop')
	mes = bot.send_message(message.chat.id, 'Придумай и напиши пароль для расписания:', reply_markup=pas_markup)
	bot.register_next_step_handler(mes, pas_write)

def	pas_write(message):
	try:
		cursor.execute("UPDATE users SET pas = '{}', status='1', lesson='1' WHERE chat_id = '{}'".format(message.text, message.chat.id))
		conn.commit()
	except:
		mes = bot.send_message(message.chat.id, 'Произошла ошибка, напиши другой пароль:')
		bot.register_next_step_handler(mes, pas_write)
	read_markup = telebot.types.ReplyKeyboardMarkup(True, False)
	read_markup.row('Перейти к следующему дню')
	read_markup.row('/stop')
	mes = bot.send_message(message.chat.id, 'Хорошо, какой у тебя 1 урок(занятие) в понедельник?(max- 8 уроков/занятий)', reply_markup=read_markup)
	bot.register_next_step_handler(mes, day_write)


def day_write(message):
	week_inf = ['во вторник', 'с среду', 'в четверг','в пятницу','в субботу']
	week_inf_eng = ['monday','tuesday','wednesday','thursday','friday','saturday']
	week_inf_rus = ['Понедельник:','Вторник:','Среда:','Четверг:','Пятница:','Суббота:']
	cursor.execute("SELECT status FROM users WHERE chat_id = {}".format(message.chat.id))
	status = int(cursor.fetchone()[0])
	cursor.execute("SELECT week FROM users WHERE chat_id = {}".format(message.chat.id))
	week = int(cursor.fetchone()[0])
	cursor.execute("SELECT lesson FROM users WHERE chat_id = {}".format(message.chat.id))
	lesson = float(cursor.fetchone()[0])
	if message.text	== '/stop':
		stop(message)
		return None
	else:
		if (lesson % 1 != 0) or message.text == 'Перейти к следующему дню' or message.text == 'Закончить создание расписания':
			if lesson != 9.0 and message.text != 'Перейти к следующему дню' and message.text != 'Закончить создание расписания':
				cursor.execute("UPDATE users SET t{}='{}' WHERE chat_id = '{}'".format(int(lesson-0.5), message.text, message.chat.id))
				mes = bot.send_message(message.chat.id, 'Какой(ое) у тебя {} урок(занятие)?'.format(int(lesson+1)))
				cursor.execute("UPDATE users SET lesson='{}' WHERE chat_id = '{}'".format(lesson+0.5, message.chat.id))
				conn.commit()
				bot.register_next_step_handler(mes, day_write)
			if message.text == 'Перейти к следующему дню' or message.text == 'Закончить создание расписания' or lesson == 9:
				if (status != week or message.text != 'Закончить создание расписания'):
					cursor.execute("UPDATE users SET lesson='1', status='{}' WHERE chat_id = '{}'".format(status+1, message.chat.id))
					cursor.execute("UPDATE users SET t8='{}' WHERE chat_id = '{}'".format(message.text, message.chat.id))
					conn.commit()
				#Создание дня в расписании
				cursor.execute("SELECT l1,l2,l3,l4,l5,l6,l7,l8 FROM users WHERE chat_id = {}".format(message.chat.id))
				lesson_day = cursor.fetchall()[0]
				cursor.execute("SELECT t1,t2,t3,t4,t5,t6,t7,t8 FROM users WHERE chat_id = {}".format(message.chat.id))
				time_day = cursor.fetchall()[0]
				cursor.execute("SELECT name_write FROM users WHERE chat_id = {}".format(message.chat.id))
				name_write = cursor.fetchone()[0]
				cursor.execute("SELECT pas FROM users WHERE chat_id = {}".format(message.chat.id))
				pas = cursor.fetchone()[0]

				c = sqlite3.connect("/home/Keltor/table/{}.sqlite".format(name_write))
				cur = c.cursor()
				try:
					cur.execute("CREATE TABLE week (week text, lesson text, pas text)")
					cur.execute("INSERT INTO week (week, pas) VALUES ('{}', '{}')".format(week,pas))
				except:
					pass
				try:
					if week == 5:
						cur.execute("CREATE TABLE schedule (monday text,tuesday text, wednesday text, thursday text, friday text)")
					else:
						cur.execute("CREATE TABLE schedule (monday text,tuesday text, wednesday text, thursday text, friday text, saturday text)")
				except:
					pass
				cur.execute("CREATE TABLE {} (lesson text, dzthis text, dznext text, time_day text)".format(week_inf_eng[status-1]))
				a=''
				for i in range(len(lesson_day)):
					if lesson_day[i]:
						try:
							a=a+str(i+1)+'.'+lesson_day[i]+'('+time_day[i]+')'+r'\n'
						except:
							a=a+str(i+1)+'.'+lesson_day[i]+'(нету)'+r'\n'
				if status == 1:
					cur.execute("INSERT INTO schedule ('{}') VALUES ('{}')".format(week_inf_eng[status-1], week_inf_rus[status-1]+r'\n'+a))
				else:
					cur.execute("UPDATE schedule SET '{}' = '{}'".format(week_inf_eng[status-1], week_inf_rus[status-1]+r'\n'+a))
				for i in lesson_day:
					if i:
						try:
							cur.execute("INSERT INTO {} (lesson, dzthis, dznext, time_day) VALUES ('{}','{}','{}','{}')".format(week_inf_eng[status-1], i, i+': ничего', i+': ничего', time_day[lesson_day.index(i)]))
							cur.execute("INSERT INTO week (lesson) VALUES ('{}')".format(i))
						except:
							cur.execute("INSERT INTO {} (lesson, dzthis, dznext, time_day) VALUES ('{}','{}','{}','{}')".format(week_inf_eng[status-1], i, i+': ничего', i+': ничего', '(нету)'))
							cur.execute("INSERT INTO week (lesson) VALUES ('{}')".format(i))
						c.commit()
					else:
						break
				if (status == week or message.text == 'Закончить создание расписания'):
					cursor.execute("UPDATE users SET l1='',l2='',l3='',l4='',l5='',l6='',l7='',l8='',t1='',t2='',t3='',t4='',t5='',t6='',t7='',t8='',user_table='{}',status='',name_write='' WHERE chat_id = '{}'".format(name_write,message.chat.id))
				else:
					cursor.execute("UPDATE users SET l1='',l2='',l3='',l4='',l5='',l6='',l7='',l8='',t1='',t2='',t3='',t4='',t5='',t6='',t7='',t8='' WHERE chat_id = '{}'".format(message.chat.id))
				conn.commit()
				c.close()

				if status==week-1:
					read_markup = telebot.types.ReplyKeyboardMarkup(True, False)
					read_markup.row('Закончить создание расписания')
					read_markup.row('/stop')
					mes = bot.send_message(message.chat.id, 'Хорошо, какой у тебя 1 урок(занятие) {}?(max- 8 уроков/занятий)'.format(week_inf[status-1]),reply_markup=read_markup)
					bot.register_next_step_handler(mes, day_write)
				elif (status == week or message.text == 'Закончить создание расписания'):
					leave_markup = telebot.types.ReplyKeyboardRemove()
					os.makedirs('/home/Keltor/Saved_data/{}'.format(name_write))
					bot.send_message(message.chat.id, 'Создание расписания закончено, теперь напиши /start !',reply_markup=leave_markup)
				else:
					mes = bot.send_message(message.chat.id, 'Хорошо, какой у тебя 1 урок(занятие) {}?(max- 8 уроков/занятий)'.format(week_inf[status-1]))
					bot.register_next_step_handler(mes, day_write)
		else:
			print(1)
			if (message.text != 'Перейти к следующему дню'):
				if message.text !='Закончить создание расписания' and lesson!=8.5:
					cursor.execute("UPDATE users SET l{}='{}' WHERE chat_id = '{}'".format(int(lesson), message.text, message.chat.id))
					mes = bot.send_message(message.chat.id, 'Напиши время занятия в формате чч:мм - чч:мм')
					print(lesson)
					cursor.execute("UPDATE users SET lesson='{}' WHERE chat_id = '{}'".format(lesson+0.5, message.chat.id))
					conn.commit()
					bot.register_next_step_handler(mes, day_write)

@bot.message_handler(commands=['disconnect'])
def disconnect(message):
	cursor.execute("UPDATE users SET user_table='',status='',week='',name_write='',lesson='',l1='',l2='',l3='',l4='',l5='',l6='',l7='',l8='' WHERE chat_id = '{}'".format(message.chat.id))
	conn.commit()
	leave_markup = telebot.types.ReplyKeyboardRemove()
	bot.send_message(message.chat.id, 'Вы покинули свое расписание ._. Присоединиться - /connect. Создать новое - /new', reply_markup = leave_markup)

@bot.message_handler(commands=['connect'])
def connect(message):
	connect_markup = telebot.types.ReplyKeyboardMarkup(True, False)
	files = os.listdir('/home/Keltor/table/')
	try:
		files.remove('.sqlite')
	except:
		pass
	for i in range(0,len(files),2):
		if (i == (len(files) - 1) ) and ((i + 1) % 2 == 1 ):
			connect_markup.row('{}'.format(files[i][:-7]),'')
		else:
			connect_markup.row('{}'.format(files[i][:-7]),'{}'.format(files[i+1][:-7]))
	connect_markup.row('/stop')
	mes = bot.send_message(message.chat.id, 'Выбери одно из существующих расписаний (кроме /stop, пожалуйста):', reply_markup=connect_markup)
	bot.register_next_step_handler(mes, conn_handler)

@bot.message_handler(commands=['subscribe'])
def subscribe(message):
	try:
		subs(message)
	except:
		start(message)

@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
	try:
		cursor.execute("UPDATE users SET subs='' WHERE chat_id = '{}'".format(message.chat.id))
		conn.commit()
		bot.send_message(message.chat.id, 'Вы отписались от рассылки расписания -_- Подписаться - /subscribe')
	except:
		start(message)

@bot.message_handler(commands=['status'])
def status(message):
	cursor.execute("SELECT subs FROM users WHERE chat_id = {}".format(message.chat.id))
	subs = cursor.fetchone()[0]
	if subs:
		bot.send_message(message.chat.id, 'Вы подписаны на рассылку')
	else:
		bot.send_message(message.chat.id, 'Вы не подписаны на рассылку')

def conn_handler(message):
	if message.text	== '/stop':
		stop(message)
		return None
	else:
		files = os.listdir('/home/Keltor/table/')
		try:
			files.remove('.sqlite')
		except:
			pass
		if (message.text + '.sqlite') in files:
			cursor.execute("UPDATE users SET name_write='{}' WHERE chat_id = '{}'".format(message.text, message.chat.id))
			conn.commit()
			pas_markup = telebot.types.ReplyKeyboardMarkup(True, False)
			pas_markup.row('/stop')
			mes = bot.send_message(message.chat.id, 'Напиши пароль для данного комплекса[расписания]:',reply_markup=pas_markup)
			bot.register_next_step_handler(mes, conn_pas)
		else:
			mes = bot.send_message(message.chat.id, 'Ошибка, выбери что-нибудь из предложенного списка:')
			bot.register_next_step_handler(mes, conn_handler)

def conn_pas(message):
	if message.text	== '/stop':
		stop(message)
		return None
	else:
		cursor.execute("SELECT name_write FROM users WHERE chat_id = {}".format(message.chat.id))
		name_write = cursor.fetchone()[0]
		c = sqlite3.connect("/home/Keltor/table/{}.sqlite".format(name_write))
		cur = c.cursor()
		cur.execute("SELECT pas FROM week")
		pas = cur.fetchone()[0]
		if message.text == pas:
			cur.execute("SELECT week FROM week")
			week = cur.fetchone()[0]
			cursor.execute("UPDATE users SET user_table = '{}', week = '{}' WHERE chat_id = '{}'".format(name_write, week, message.chat.id))
			conn.commit()
			bot.send_message(message.chat.id, 'Вы присоединились к комлексу {}'.format(name_write))
			start(message)
		else:
			mes = bot.send_message(message.chat.id, 'Пароль неверен! Напиши правильный или нажми на /stop:',reply_markup=pas_markup)
			bot.register_next_step_handler(mes, conn_pas)

###Разные типы контента

@bot.message_handler(content_types=['document', 'audio', 'sticker', 'photo', 'video', 'voice'])
def cont(message):
	bot.send_message(message.chat.id, text = 'Ну и зочем ты мне это скинул?')

### Команды из главного меню


######
######
###### Просмотр расписания
@bot.message_handler(regexp='Расписание')
def raspis(message):
	schedule_markup = telebot.types.ReplyKeyboardMarkup(True, False)
	schedule_markup.row('На понедельник', 'На вторник', 'На среду')
	cursor.execute("SELECT week FROM users WHERE chat_id = {}".format(message.chat.id))
	week = cursor.fetchone()[0]
	if week == '5':
		schedule_markup.row('На четверг', 'На пятницу', 'На всю неделю')
	else:
		schedule_markup.row('На четверг', 'На пятницу','На субботу', 'На всю неделю')
	schedule_markup.row('Вернуться на начальную страницу', 'Подписаться на рассылку расписания')
	bot.send_message(message.chat.id, 'Выбери день:', reply_markup=schedule_markup)


@bot.message_handler(regexp='Вернуться на начальную страницу')
def back(message):
	start(message)


@bot.message_handler(regexp='Подписаться на рассылку расписания')
def subs(message):
	try:
		cursor.execute("SELECT user_table FROM users WHERE chat_id = {}".format(message.chat.id))
		user_table = cursor.fetchone()[0]
		cursor.execute("UPDATE users SET subs='{}' WHERE chat_id = '{}'".format(user_table, message.chat.id))
		conn.commit()
		cursor.execute("SELECT week FROM users WHERE chat_id = {}".format(message.chat.id))
		week = cursor.fetchone()[0]
		if week == '5':
			bot.send_message(message.chat.id, 'Ежедневно(кроме сб и вс), вы будете получать в 7:45(по мск) расписание на день\n Можете отписаться - /unsubscribe')
		else:
			bot.send_message(message.chat.id, 'Ежедневно(кроме вс), вы будете получать в 7:45(по мск) расписание на день\n Можете отписаться - /unsubscribe')
	except:
		start(message)
######
######
###### Просмотр дз
@bot.message_handler(regexp='Просмотр дз на данную неделю')
def view_dz(message):
	schedule_markup = telebot.types.ReplyKeyboardMarkup(True, False)
	schedule_markup.row('Понедельник', 'Вторник', 'Среда')
	cursor.execute("SELECT week FROM users WHERE chat_id = {}".format(message.chat.id))
	week = cursor.fetchone()[0]
	cursor.execute("UPDATE users SET status='1' WHERE chat_id = '{}'".format(message.chat.id))
	conn.commit()
	if week == '5':
		schedule_markup.row('Четверг', 'Пятница')
	else:
		schedule_markup.row('Четверг', 'Пятница','Суббота')
	schedule_markup.row('Вернуться на начальную страницу')
	bot.send_message(message.chat.id, 'Выбери день:', reply_markup=schedule_markup)

@bot.message_handler(regexp='Просмотр дз на следующую неделю')
def view_dz(message):
	schedule_markup = telebot.types.ReplyKeyboardMarkup(True, False)
	schedule_markup.row('Понедельник', 'Вторник', 'Среда')
	cursor.execute("SELECT week FROM users WHERE chat_id = {}".format(message.chat.id))
	week = cursor.fetchone()[0]
	cursor.execute("UPDATE users SET status='2' WHERE chat_id = '{}'".format(message.chat.id))
	conn.commit()
	if week == '5':
		schedule_markup.row('Четверг', 'Пятница')
	else:
		schedule_markup.row('Четверг', 'Пятница','Суббота')
	schedule_markup.row('Вернуться на начальную страницу')
	bot.send_message(message.chat.id, 'Выбери день:', reply_markup=schedule_markup)

#####
#####
##### Заполнение дз
@bot.message_handler(regexp='Заполнить дз на данную неделю')
def dz(message):
	try:
		schedule_markup = telebot.types.ReplyKeyboardMarkup(True, False)
		schedule_markup.row('Понедельник', 'Вторник', 'Среда')
		cursor.execute("SELECT week FROM users WHERE chat_id = {}".format(message.chat.id))
		week = cursor.fetchone()[0]
		cursor.execute("UPDATE users SET status='11' WHERE chat_id = '{}'".format(message.chat.id))
		conn.commit()
		if week == '5':
			schedule_markup.row('Четверг', 'Пятница')
		else:
			schedule_markup.row('Четверг', 'Пятница','Суббота')
		schedule_markup.row('Вернуться на начальную страницу')
		bot.send_message(message.chat.id, 'Выбери день:', reply_markup=schedule_markup)
	except:
		start(message)

@bot.message_handler(regexp='Заполнить дз на следующую неделю')
def dz(message):
	try:
		schedule_markup = telebot.types.ReplyKeyboardMarkup(True, False)
		schedule_markup.row('Понедельник', 'Вторник', 'Среда')
		cursor.execute("SELECT week FROM users WHERE chat_id = {}".format(message.chat.id))
		week = cursor.fetchone()[0]
		cursor.execute("UPDATE users SET status='22' WHERE chat_id = '{}'".format(message.chat.id))
		conn.commit()
		if week == '5':
			schedule_markup.row('Четверг', 'Пятница')
		else:
			schedule_markup.row('Четверг', 'Пятница','Суббота')
		schedule_markup.row('Вернуться на начальную страницу')
		bot.send_message(message.chat.id, 'Выбери день:', reply_markup=schedule_markup)
	except:
		start(message)

@bot.message_handler(regexp='Вернуться на предыдущую страницу')
def dz(message):
	try:
		cursor.execute("UPDATE users SET lesson='' WHERE chat_id = '{}'".format(message.chat.id))
		conn.commit()
		schedule_markup = telebot.types.ReplyKeyboardMarkup(True, False)
		schedule_markup.row('Понедельник', 'Вторник', 'Среда')
		cursor.execute("SELECT week FROM users WHERE chat_id = {}".format(message.chat.id))
		week = cursor.fetchone()[0]
		if week == '5':
			schedule_markup.row('Четверг', 'Пятница')
		else:
			schedule_markup.row('Четверг', 'Пятница','Суббота')
		schedule_markup.row('Вернуться на начальную страницу')
		bot.send_message(message.chat.id, 'Выбери день:', reply_markup=schedule_markup)
	except:
		start(message)

@bot.message_handler(regexp='Архив д/з')
def arch(message):
	try:
		arch_markup = telebot.types.ReplyKeyboardMarkup(True, False)
		arch_markup.row('Сентябрь', 'Октябрь','Ноябрь')
		arch_markup.row('Декабрь', 'Январь','Февраль')
		arch_markup.row('Март', 'Апрель','Май')
		arch_markup.row('Вернуться на начальную страницу')
		mes = bot.send_message(message.chat.id, text = 'Выберите месяц:' ,reply_markup=arch_markup)
		bot.register_next_step_handler(mes, arch2)
	except:
		start(message)

def arch2(message):
	Monat = {'Сентябрь':'Sep','Октябрь':'Oct','Ноябрь':'Nov','Декабрь':'Dec','Январь':'Jan','Февраль':'Feb','Апрель':'Apr','Май':'May', 'Март':'Mar'}
	if message.text == '/stop':
		stop(message)
		return None
	elif message.text == '/start' or message.text == 'Вернуться на начальную страницу':
		start(message)
		return None
	elif message.text == '/disconnect':
		disconnect(message)
		return None
	else:
		if message.text in Monat:
			cursor.execute("SELECT user_table FROM users WHERE chat_id = {}".format(message.chat.id))
			user_table = cursor.fetchone()[0]
			filesNoMonat = os.listdir('/home/Keltor/Saved_data/{}'.format(user_table))
			files = []
			for i in filesNoMonat:
				if Monat[message.text] in i:
					files.append(i)
			arch_markup = telebot.types.ReplyKeyboardMarkup(True, False)
			for i in range(0,len(files),2):
				if (i == (len(files) - 1) ) and ((i + 1) % 2 == 1 ):
					arch_markup.row('{}'.format(files[i]),'')
				else:
					arch_markup.row('{}'.format(files[i]),'{}'.format(files[i+1]))
			arch_markup.row('Вернуться на выбор месяца', 'Вернуться на начальную страницу')
			mes =bot.send_message(message.chat.id, text = 'Выберите файл:' ,reply_markup=arch_markup)
			bot.register_next_step_handler(mes, arch3)
		else:
			mes = bot.send_message(message.chat.id, text = 'Не понял твое сообщение, выбери месяц:')
			bot.register_next_step_handler(mes, arch2)

def arch3(message):
	if message.text == '/stop':
		stop(message)
		return None
	elif message.text == '/start' or message.text == 'Вернуться на начальную страницу':
		start(message)
		return None
	elif message.text == '/disconnect':
		disconnect(message)
		return None
	elif message.text == 'Вернуться на выбор месяца':
		arch(message)
		return None
	else:
		try:
			cursor.execute("SELECT user_table FROM users WHERE chat_id = {}".format(message.chat.id))
			user_table = cursor.fetchone()[0]
			files = os.listdir('/home/Keltor/Saved_data/{}'.format(user_table))
			if message.text in files:
				with open('/home/Keltor/Saved_data/{}/{}'.format(user_table, message.text), 'r') as f:
					arh = f.read()
				mes = bot.send_message(message.chat.id, text = 'Файл {}\n'.format(message.text) + arh)
				bot.register_next_step_handler(mes, arch3)
		except:
			mes = bot.send_message(message.chat.id, 'Ничего не понимаю. Напиши /start !')
			bot.register_next_step_handler(mes, arch3)

@bot.message_handler(content_types=['text'])
def glob(message):
	cursor.execute("SELECT chat_id FROM users WHERE chat_id = '{}'".format(message.chat.id))
	row = cursor.fetchone()
	if not row:
		cursor.execute("INSERT INTO users (chat_id, username) VALUES ('{}','{}')".format(message.chat.id, message.chat.username))
		conn.commit()
	else:
		days = ['Понедельник','Вторник','Среда','Четверг','Пятница','Суббота']
		daysdict = {'Понедельник':'monday', 'Вторник':'tuesday', 'Среда':'wednesday', 'Четверг':'thursday', 'Пятница':'friday', 'Суббота':'saturday'}
		schedule = {'На понедельник':'monday','На вторник':'tuesday','На среду':'wednesday','На четверг':'thursday','На пятницу':'friday','На субботу':'saturday','На всю неделю':1}
		try:
			cursor.execute("SELECT user_table FROM users WHERE chat_id = {}".format(message.chat.id))
			user_table = cursor.fetchone()[0]
			c = sqlite3.connect("/home/Keltor/table/{}.sqlite".format(user_table))
			cur = c.cursor()
			cur.execute("SELECT DISTINCT lesson FROM week")
			lesson = []
			row = cur.fetchall()
			for i in range(len(row)):
				if i:
					lesson.append(row[i][0])
		except:
			start(message)
			return None
		try:
			cursor.execute("SELECT status FROM users WHERE chat_id = {}".format(message.chat.id))
			status = int(cursor.fetchone()[0])
			cursor.execute("SELECT lesson FROM users WHERE chat_id = '{}'".format(message.chat.id))
			leswrite = cursor.fetchone()[0]
		except:
			status = None
			leswrite = ''
		if message.text in schedule:
			try:
				cursor.execute("SELECT user_table FROM users WHERE chat_id = {}".format(message.chat.id))
				user_table = cursor.fetchone()[0]

				c = sqlite3.connect("/home/Keltor/table/{}.sqlite".format(user_table))
				cur = c.cursor()
				if message.text == 'На всю неделю':
					cur.execute("SELECT * FROM schedule")
					msg = cur.fetchall()
					for i in msg[0]:
						bot.send_message(message.chat.id, eval('"%s"' % i))
				else:
					cur.execute("SELECT {} FROM schedule".format(schedule[message.text]))
					msg = eval('"%s"' % cur.fetchone()[0])
					bot.send_message(message.chat.id, msg)
			except:
				start(message)
				return None
		elif message.text in days:
			try:
				if status == 11 or status == 22:
					c = sqlite3.connect("/home/Keltor/table/{}.sqlite".format(user_table))
					cur = c.cursor()
					cur.execute("SELECT DISTINCT lesson FROM {}".format(daysdict[message.text]))
					cursor.execute("UPDATE users SET day='{}' WHERE chat_id = '{}'".format(daysdict[message.text],message.chat.id))
					conn.commit()
					lesson = cur.fetchall()
					write_markup = telebot.types.ReplyKeyboardMarkup(True, False)
					for i in range(0,len(lesson),3):
						if (i == (len(lesson) - 1) ) and (i % 2 == 0 ):
							write_markup.row('{}'.format(lesson[i][0]))
						else:
							try:
								write_markup.row(lesson[i][0],lesson[i+1][0], lesson[i+2][0])
							except:
								write_markup.row(lesson[i][0],lesson[i+1][0])
					write_markup.row('Вернуться на предыдущую страницу', 'Вернуться на начальную страницу')
					bot.send_message(message.chat.id, 'Выбери урок:', reply_markup=write_markup)
				else:
					c = sqlite3.connect("/home/Keltor/table/{}.sqlite".format(user_table))
					cur = c.cursor()
					bot.send_message(message.chat.id, '{}:\n'.format(message.text))
					if status == 1:
						cur.execute("SELECT dzthis FROM {}".format(daysdict[message.text]))
						row = cur.fetchall()
						for i in range(len(row)):
							bot.send_message(message.chat.id, str(i+1) + '.' + row[i][0] + '\n')
					else:
						cur.execute("SELECT dznext FROM {}".format(daysdict[message.text]))
						row = cur.fetchall()
						for i in range(len(row)):
							bot.send_message(message.chat.id, str(i+1) + '.' + row[i][0] + '\n')
			except:
				start(message)
		elif message.text in lesson:
			cursor.execute("UPDATE users SET lesson='{}' WHERE chat_id = '{}'".format(message.text, message.chat.id))
			conn.commit()
			bot.send_message(message.chat.id, 'Напиши дз:')
		elif leswrite:
			cursor.execute("SELECT day FROM users WHERE chat_id = '{}'".format(message.chat.id))
			day = cursor.fetchone()[0]
			c = sqlite3.connect("/home/Keltor/table/{}.sqlite".format(user_table))
			cur = c.cursor()
			cursor.execute("UPDATE users SET lesson='' WHERE chat_id = '{}'".format(message.chat.id))
			conn.commit()
			if status == 11:
				cur.execute("UPDATE {} SET dzthis='{}' WHERE lesson = '{}'".format(day, leswrite+': '+message.text, leswrite))
				c.commit()
				bot.send_message(message.chat.id, 'Дз записано!')
			elif status == 22:
				cur.execute("UPDATE {} SET dznext='{}' WHERE lesson = '{}'".format(day, leswrite+': '+message.text, leswrite))
				c.commit()
				bot.send_message(message.chat.id, 'Дз записано!')
			else:
				start(message)
		else:
			bot.send_message(message.chat.id, 'Ничего не понимаю. Напиши /start !')

if __name__ == '__main__':
	app.run()