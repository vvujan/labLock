#! /usr/bin/python

import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time

broker = "BROKER IP/ADDR"
username = "MQTT USER"
password = "MQTT PASS"
inTopic = "/door/rfid"
outTopic = "/door/lock"
configFile = "labLock.conf"
timestamp = 0
doorInput = ""

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

def unlock():
	client.publish(outTopic,"4")

def epoch():
	epochTime = int(time.time())
	return epochTime

def addUser(doorInput):
	with open(configFile) as json_file:
		data = json.load(json_file)
		newUser = "user" + str(len(data['lock']) +1)
		data["lock"].append({newUser : "addedbyKey", 'isAdmin': False, 'key': doorInput})
		with open(configFile, 'w') as f:
			json.dump(data, f)

def keyEval(doorInput):
	with open(configFile) as json_file:  
		data = json.load(json_file)
	for p in data['lock']:
		listItem = p['key']
		isAdmin = p ['isAdmin']

		if doorInput == listItem and isAdmin == True:
			unlock()
			global timestamp
			global found 
			timestamp = epoch()
			found = True
			print "admin"
			break
		elif doorInput == listItem and isAdmin == False:
			unlock()
			found = True
			timestamp = 0
			print "user"
			break
		elif doorInput != listItem:
			found = False
	if timestamp >= int(time.time()) - 5 and found == False: 
		addUser(doorInput)
		timestamp = 0
		print str(doorInput) + " key added"

client.loop_forever()
