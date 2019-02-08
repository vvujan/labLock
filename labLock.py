#! /usr/bin/python

import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
import commands

#need to add:
#	#Registration,#unlock,log


doorInput = ""
broker = "" #add broker here - example: "mqtt.hacklabos.org"
username = "" #add username here
password = "" #add password here
inTopic = "/door/rfid"
outTopic = "/door/lock"
configFile = "labLock.conf"
timestamp = 0


#MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(inTopic)
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    doorInput = str(msg.payload)
    keyEval(doorInput)

def on_publish(client, userdata, mid):
    print("mid: "+str(mid))
 
client = mqtt.Client()
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, 1883, 60)

def unlock(userName, userId):
	client.publish(outTopic,"4")
	#commands.getoutput('mpc play') #optional - enable mpc player
	#commands.getoutput('scripts/smart_lock_log.sh ' + userName + ' ' + userId) #optional - call script for the logging data

def epoch():
	epochTime = int(time.time())
	return epochTime

def addUser(doorInput):
	with open(configFile) as json_file:
		data = json.load(json_file)
		cardId = str(len(data['lock']) +1)
		data["lock"].append({"id": cardId, "user" : "addedbyKey", 'isAdmin': False, 'key': doorInput})
		with open(configFile, 'w') as f:
			json.dump(data, f)

def keyEval(doorInput):
	loopState	=	False
	with open(configFile) as json_file:
		data = json.load(json_file)
	for p in data['lock']:
		cardKey = p['key']
		userId = p['id']
		isAdmin = p ['isAdmin']
		userName = p['user']

		if doorInput == cardKey and isAdmin == True:
			unlock(userName, userId)
			global timestamp
			timestamp = epoch()
			global found 
			found = True
			print "admin"
			break
		elif doorInput == cardKey and isAdmin == False:
			unlock(userName, userId)
			found = True
			timestamp = 0
			print "user"
			break
		elif doorInput != cardKey:
			found = False
	if timestamp >= int(time.time()) - 5 and found == False: 
		addUser(doorInput)
		timestamp = 0
		print str (doorInput) + " key added"

client.loop_forever()
