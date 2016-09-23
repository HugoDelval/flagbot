#!/usr/bin/python3
from slacker import Slacker
import ctftime
import sqlite3
import time
import sys
from datetime import datetime


CHANNEL_ANNONCE='C2F0CAZQ9'
CTF_COMMANDS=['ctf','play','hack']
conn=sqlite3.connect('/root/slackbot/flagbot.db')
db=conn.cursor()
slack=Slacker('xoxb-82968660485-8TXMs4NswNdQxI1pJ4kXSxww')


def exec_db_script(filename):
	fi=open(filename,'r')
	for line in fi.readlines():
		print('[SQLite] Executing : '+line.strip())
		db.execute(line.strip())
	fi.close()
	conn.commit()

def get_check_timestamp():
	for res in db.execute('SELECT timestamp FROM checktimestamp'):
		return float(res[0])

def set_check_timestamp(ts):
	if type(ts)!=type(1.0):
		print('timestamp format error : got >'+str(ts)+'<, expected float')
		return
	db.execute('DELETE FROM checktimestamp')
	db.execute('INSERT INTO checktimestamp VALUES(\''+str(ts)+'\')')
	conn.commit()

def get_unread():
	ts=time.time()
	res=slack.channels.history(CHANNEL_ANNONCE,oldest=int(get_check_timestamp())).body['messages']
	set_check_timestamp(ts)
	return res

def participate_ctf(message):
	eventid=message['text'].split()[1]
	print(ctftime.get_event(int(eventid)))

def info_ctf(message):
	eventid=message['text'].split()[1]
	event=ctftime.get_event(int(eventid))
	datestart = datetime.strptime(event.start_ts,"%Y-%m-%dT%H:%M:%S+00:00")
	dateend = datetime.strptime(event.finish_ts,"%Y-%m-%dT%H:%M:%S+00:00")
	print(datestart)
	tsstart=time.mktime(datestart.timetuple())
	tsend=time.mktime(dateend.timetuple())
	slack.chat.post_message(CHANNEL_ANNONCE,event.title+' '+str(tsstart)+' '+str(tsend))
	
def process(message):
	for x in CTF_COMMANDS:
		if message['text'].startswith('!'+x+' '):
			participate(message)
	if message['text'].startswith('!info'):
		info_ctf(message)

exec_db_script('/root/slackbot/flagbot.sql')

while True:
	unread=get_unread()
	for message in unread:
		process(message)
	time.sleep(5)
