#!/usr/bin/python3
from slacker import Slacker
import ctftime
import sqlite3
import time
import sys
from datetime import datetime
import json
import pytz
from dateutil.parser import parse
import math


CTF_COMMANDS=['ctf','play','hack']
conn=sqlite3.connect('/root/slackbot/flagbot.db')
db=conn.cursor()
with open('/root/slackbot/config.json') as f:
	config = json.loads(f.read())
	slack_token = config['slack_token']
	CHANNEL_ANNONCE = config['CHANNEL_ANNONCE']
slack=Slacker(slack_token)


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
		raise Exception('timestamp format error : got >'+str(ts)+'<, expected float')
		return
	db.execute('DELETE FROM checktimestamp')
	db.execute('INSERT INTO checktimestamp VALUES(\''+str(ts)+'\')')
	conn.commit()


def get_unread():
	ts=time.time()
	res=slack.channels.history(CHANNEL_ANNONCE,latest=int(ts),oldest=int(get_check_timestamp())).body['messages']
	set_check_timestamp(ts)
	return res


def get_participate():
	ctflist=[]
	for res in db.execute('SELECT * FROM participate'):
		if len(res)!=4:
			raise Exception('Invalid number of columns for participate')
		ctflist.append({'id':res[0],'start':res[1],'end':res[2],'lastreminded':res[3]})
	return ctflist


def get_participate_ids():
        idlist=[]
        for res in db.execute('SELECT * FROM participate'):
                if len(res)!=4:
                        raise Exception('Invalid number of columns for participate')
                idlist.append(res[0])
        return idlist


def participate_db(ctfId, begints, endts):
	db.execute('INSERT INTO participate VALUES ('+str(int(ctfId))+','+str(int(begints))+','+str(int(endts))+','+str(int(time.time()))+')')
	conn.commit()


def participate_ctf(message):
	eventid=int(message['text'].split()[1])
	event=ctftime.get_event(eventid)
	if eventid in get_participate_ids():
		slack.chat.post_message(CHANNEL_ANNONCE,'Already registered to CTF '+event.title)
	else:
		datestart=parse(event.start_ts)
		dateend=parse(event.finish_ts)
		tsstart=datestart.timestamp()
		tsend=dateend.timestamp()
		if time.time()>tsend:
			slack.chat.post_message(CHANNEL_ANNONCE,'CTF '+event.title+' has already ended.')
		else:
			participate_db(eventid,tsstart,tsend)
			slack.chat.post_message(CHANNEL_ANNONCE,'Successfully registered to CTF !')
			info_ctf(message)


def wdh_from_delta(delta):
	delta=abs(int(delta))
	deltaW=int(delta/(7*24*60*60))
	deltaD=int(delta/(24*60*60))%7
	deltaH=int(delta/(60*60))%24
	res=''
	if deltaW:
		res+=str(deltaW)+'w '
	if deltaD:
		res+=str(deltaD)+'d '
	if deltaH:
		res+=str(deltaH)+'h '
	if res=='':
		res='0h '
	return res[:-1]


def extract_info_event(event):
	datestart = parse(event.start_ts)
	dateend = parse(event.finish_ts)
	tsstart=datestart.timestamp()
	tsend=dateend.timestamp()
	currts=time.time()
	if currts<tsstart:
		delta=int(tsstart-currts)
		deltaHtot=int(delta/(60*60))
		msgtime='CTF will start in '
		if deltaHtot==0:
			msgtime='CTF is starting soon !'
		else:
			msgtime='CTF will start in '+wdh_from_delta(delta)
	elif tsstart<=currts<tsend:
		msgtime='CTF ends in '+wdh_from_delta(tsend-currts)
	else:
		msgtime='CTF ended '+wdh_from_delta(currts-tsend)+' ago'
	return msgtime


def info_ctf(message):
	eventid=message['text'].split()[1]
	event=ctftime.get_event(int(eventid))
	msgtime = extract_info_event(event)
	slack.chat.post_message(CHANNEL_ANNONCE,event.title+"\n"+msgtime)

	
def process(message):
	for x in CTF_COMMANDS:
		if message['text'].startswith('!'+x+' '):
			participate_ctf(message)
	if message['text'].startswith('!info'):
		info_ctf(message)


def fetch_next_events():
	upcomming_events = ctftime.get_next_events()
	if upcomming_events:
		slack.chat.post_message(CHANNEL_ANNONCE, "Hey @channel, there is upcoming CTFs !!")
	for event in upcomming_events:
		msgtime = extract_info_event(event)
		slack.chat.post_message(CHANNEL_ANNONCE, event.title+"\n"+msgtime)


exec_db_script('/root/slackbot/flagbot.sql')
last_timestamp_fetch_next_events = 0

try:
	while True:
		unread=get_unread()
		for message in unread:
			try:
				process(message)
			except ValueError as e:
				slack.chat.post_message(CHANNEL_ANNONCE, "Oh come on! Stop playing :p. You've triggered a cast error.")
		time.sleep(2)
		if last_timestamp_fetch_next_events < time.time() - 3*24*60*60:
			fetch_next_events()
			last_timestamp_fetch_next_events = time.time()
except:
	import os
	os.remove('/var/run/flagbot.pid')
