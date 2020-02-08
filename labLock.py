#! /usr/bin/python
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
import commands
import sqlite3
import datetime
import config
from enum import Enum

key = ""
broker = config.MQTT_CONFIG['broker']
username = config.MQTT_CONFIG['username']
password = config.MQTT_CONFIG['password']
inTopic = config.MQTT_CONFIG['inTopic']
outTopic = config.MQTT_CONFIG['outTopic']
timestamp = 0
date = datetime.datetime.now()

#MQTT

def on_connect(client, userdata, flags, rc):
   print("Connected with result code "+str(rc))
   client.subscribe(inTopic)
def on_message(client, userdata, msg):
   print(msg.topic+" "+str(msg.payload))
   key = str(msg.payload)
   keyEval(key)
   time.sleep(2)

def on_publish(client, userdata, mid):
   print("mid: "+str(mid))

client = mqtt.Client()
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, 1883, 60)

#enums
class roles(Enum):
    user = 0
    admin = 1
    inactive = 2

class actions(Enum):
    login = 0
    logout = 1
    registration = 2
    invalid_login = 3

#SQL
def dbconnect():
    # Create a database in RAM
    db = sqlite3.connect(config.DATABASE_CONFIG['memoryOrDisk'])
    # Creates or opens a file called mydb with a SQLite3 DB
    db = sqlite3.connect(config.DATABASE_CONFIG['pathToDatabase'])
    db.isolation_level = None
    #print "Connected to database " + config.DATABASE_CONFIG['pathToDatabase']
    cursor = db.cursor()
    return db,cursor


def closeConnection():
    db.close()
    print "Database connection closed"

#login
def login(key):
    db,cursor=dbconnect()
    user_data= cursor.execute('''SELECT id, username from users where key= ?''',[key])
    user_data = cursor.fetchone()
    if (user_data > 0):
        id = user_data[0]
        print "User with id " + str(id) + " is successfully logged in"
        addLog(db, cursor, id, date, actions.login.value, "valid loggin")
        unlock(db,cursor,id)
        prevRole = checkRole(id)
    else:
        comment="invalid log with key " + key
        print comment
        addLog(db,cursor,key,date,3,comment)
        print "Username with " + key + " doesn't exist"
        timestamp = 0
        return 0
    db.close()

#
def unlock(db,cursor,id):
    db,cursor=dbconnect()
    userName= cursor.execute('''SELECT username from users where id= ?''',[id])
    userName = cursor.fetchone()
    userName = userName[0]
    print userName
    config.DATABASE_CONFIG['memoryOrDisk']
    client.publish(config.MQTT_CONFIG['outTopic'],"4")
    commands.getoutput('mpc play')
    commands.getoutput('scripts/smart_lock_log.sh ' + userName)
    timestamp = config.MQTT_CONFIG['timestamp']
    db.close()

def checkRole(id):
    db,cursor=dbconnect()
    role= cursor.execute('''SELECT roles from users where id= ?''',[id])
    role = cursor.fetchone()
    db.close()
    timestamp = epoch()
    return role

def registration(timestamp, key, date, userid):
    if timestamp >= int(time.time()) - 5: #and found == False:
        action = 2
        comment = "Added by user" + userid
        addUser(db, cursor, userid, date, action, comment)
        timestamp = 0
        print str (key) + " key added"
    addUser()


def epoch():
	epochTime = int(time.time())
	return epochTime

def keyEval(key):
    login(key)


def selectLastRecord(id):

    print action
    return action

def addUser(key, date, userid):
    userid=selectLastId()+1
    roles=0
    addedby=userid
    username='user'
    cursor.execute('''INSERT INTO users(id, username, key, roles,addedby,created)
                      VALUES(?,?,?,?,?,?)''', (userid,username, key, roles,addedby,date))
    db.commit()
    db.close()

def checkDatabase():
    db,cursor=dbconnect()
    try:
        resultset = cursor.execute("SELECT 1 FROM users LIMIT 1;")
        print resultset
    except sqlite3.ProgrammingError as e:
        print e
    db.close()
    print "Database connection closed!"

def addLog(db,cursor,userid, date,action,comment):
    cursor.execute('''INSERT INTO log(usernameid, logdatetime, action, comment)
                              VALUES(?,?,?,?)''', (userid, date, action, comment))
    db.commit()
    print "Added log"

def logout(id):
    db,cursor = dbconnect()
    action = 1
    addLog(db, cursor, id, date, action, comment)
    db.close()
    print "User with id: " + id + "action: " + action

def count(rowName, tableName):
    result= cursor.execute("SELECT count(id) from users")
    result = cursor.fetchone()
    result = result[0]
    print result

client.loop_forever()
