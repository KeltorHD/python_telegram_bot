# -*- coding: utf-8 -*-
import sqlite3
import time
import os
import telebot
import constants

bot = telebot.TeleBot(constants.token, threaded=False)

week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
days = {'monday':'Пoнедельник:', 'tuesday':'Втoрник:', 'wednesday':'Срeда:', 'thursday':'Чeтвeрг:', 'friday':'Пятницa:', 'saturday':'Суббота'}
dayssche = {'Mon':'monday:', 'Tue':'tuesday:', 'Wed':'wednesday:', 'Thu':'thursday:', 'Fri':'friday:', 'Sat':'saturday'}

c = sqlite3.connect('data.sqlite')
cur = c.cursor()
files = os.listdir('/home/Keltor/table')
try:
	files.remove('.sqlite')
except:
	pass
for i in range(len(files)):
	files[i] = files[i].replace('/','')


for i in files:
	if time.ctime()[:3] == 'Sun':
		f = open('/home/Keltor/Saved_data/{}/{}.txt'.format(i[:-7], time.ctime()[4:10]), 'a')
		conn = sqlite3.connect('/home/Keltor/table/{}'.format(i))
		cursor = conn.cursor()
		for d in week:
			try:
				cursor.execute("SELECT dzthis FROM '{}'".format(d))
				row = cursor.fetchall()
				f.write('{}'.format(days[d] + '\n'))
				for k in range(len(row)):
					f.write('{}'.format(row[k][0] + '\n'))
			except:
				pass
		for d in week:
			try:
				cursor.execute("SELECT lesson FROM '{}'".format(d))
				lesson = cursor.fetchall()
				for k in range(len(lesson)):
					cursor.execute("SELECT dznext FROM '{}' WHERE lesson = '{}'".format(d, lesson[k][0]))
					dz = cursor.fetchone()
					cursor.execute("UPDATE '{}' SET dzthis = '{}' WHERE lesson = '{}'".format(d, dz[0], lesson[k][0]))
					conn.commit()
					cursor.execute("UPDATE '{}' SET dznext = '{}' WHERE lesson = '{}'".format(d, lesson[k][0] + ': Ничего', lesson[k][0]))
					conn.commit()
			except:
				pass
		conn.close()
		print('Дз перенесено')
	else:
		print('Не сегодня!')

cur.execute("SELECT subs FROM users")
Subs = cur.fetchall()
cur.execute("SELECT chat_id FROM users")
cid = cur.fetchall()
cur.execute("SELECT user_table FROM users")
nametab = cur.fetchall()
sche = {'Mon': 'monday', 'Tue':'tuesday', 'Wed':'wednesday', 'Thu': 'thursday', 'Fri': 'friday', 'Sat':'saturday'}
ten = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
if time.ctime()[:3] != 'Sun':
	for i in range(len(cid)):
		cur.execute("SELECT week FROM users WHERE chat_id = '{}'".format(cid[i][0]))
		week = cur.fetchone()[0]
		if week == '5' and time.ctime()[:3] != 'Sun' and time.ctime()[:3] != 'Sat':
			if Subs[i][0] == nametab[i][0]:
				conn = sqlite3.connect('/home/Keltor/table/{}.sqlite'.format(nametab[i][0]))
				cursor = conn.cursor()
				cursor.execute("SELECT * FROM schedule")
				row = cursor.fetchone()
				abc = eval('"%s"' % row[ten.index(sche[time.ctime()[:3]])])
				bot.send_message(cid[i][0], text = 'Вот твое расписание на сегодня, удачи в бою, сынок!\n' + abc)
				conn.close()
		elif week == '6' and time.ctime()[:3] != 'Sun':
			if Subs[i][0] == nametab[i][0]:
				conn = sqlite3.connect('/home/Keltor/table/{}.sqlite'.format(nametab[i][0]))
				cursor = conn.cursor()
				cursor.execute("SELECT * FROM schedule")
				row = cursor.fetchone()
				abc = eval('"%s"' % row[ten.index(sche[time.ctime()[:3]])])
				bot.send_message(cid[i][0], text = 'Вот твое расписание на сегодня, удачи в бою, сынок!\n' + abc)
				conn.close()

###/home/Keltor/venv/bin/python /home/Keltor/reload.py