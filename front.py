from flask import Flask, render_template
import threading
import paho.mqtt.client as mqtt
import configparser
import os
import random
import json
import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

#Path = C:\Users\Miska\Documents\AUT840\templates
configfile = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
configfile = os.path.join(configfile,'Documents')
configfile = os.path.join(configfile,'AUT840')
configfile = os.path.join(configfile,'config.ini')

config = configparser.ConfigParser()
config.sections()
config.read(configfile)

rid = 1
devId = -1
state = 'Null'
time = 'Null'
status = {'deviceId':devId, 'state': state, 'time':time}

conn = sqlite3.connect(':memory:',check_same_thread=False)
conn.row_factory = dict_factory
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS robot;")
c.execute("""CREATE TABLE IF NOT EXISTS robot (
            id INTEGER PRIMARY KEY,
            devId text,
            state text,
            time text
            );""")

def connect_mqtt(broker, port, client_id, DEBUG) -> mqtt:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client, topic):
    global devId,state,time,status
    def on_message(client, userdata, msg):
        global devId,state,time,status
        #print(f"Received {msg.payload.decode()} from {msg.topic} topic")
        m_in = json.loads(msg.payload.decode()) #decode json data
        devId = m_in['deviceId']
        state = m_in['state']
        time = m_in['time']
        insert_robot(devId, state, time)
        #robots = get_robots_state_by_id(1)
        #print(robots['state'])
    client.subscribe(topic)
    client.on_message = on_message

#CREATE
def insert_robot(devId, state, time):
    with conn:
        c.execute("INSERT or IGNORE INTO robot VALUES (:id, :devId, :state, :time)", {'id': rid, 'devId': devId, 'state': state, 'time': time})
        update_robot(devId,state,time)

#READ
def get_robots_status_by_id(id):
    sqlSt= f'SELECT * FROM robot WHERE id={id}'
    c.execute(sqlSt)
    fetch = c.fetchone()
    return fetch

#READ
def get_all_robots():
    #c.execute("SELECT * FROM robot WHERE brand=:brand", {'brand': brand})
    sqlSt="SELECT * FROM robot WHERE 1"
    c.execute(sqlSt)
    #print(c.fetchall())
    return c.fetchall()

#UPDATE
def update_robot(devId, state, time):
    with conn:
        c.execute("""UPDATE robot SET state = :state, time = :time
                    WHERE devId = :devId""",
                  {'devId': devId,'state':state, 'time':time})

#DELETE
def remove_robot(devId):
    with conn:
        c.execute("DELETE from robot WHERE deviceId = :id",
                  {'devId': devId})
    
def run():
    DEBUG = 0
    if DEBUG == 1:
        broker = str(config['DEBUG']['mqtt_broker'])
        port = int(config['DEBUG']['mqtt_port'])
        topic = config['DEBUG']['topic']
        client_id = f'python-mqtt-{random.randint(0, 100)}'
    else:
        broker = str(config['CONNECTION']['mqtt_broker'])
        port = int(config['CONNECTION']['mqtt_port'])
        client_id = 'Group-AaroLeeviMiska'
        topic = f'ii22/telemetry/{rid}'

    print(f'Connecting to {broker} : {port}')
    client = connect_mqtt(broker=broker, port=port, client_id=client_id, DEBUG=DEBUG)
    subscribe(client, topic)
    client.loop_forever()  # Start networking daemon

threadStarted=False

#Path = C:\Users\Miska\Documents\AUT840\templates
template_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
template_dir = os.path.join(template_dir,'Documents')
template_dir = os.path.join(template_dir,'AUT840')
template_dir = os.path.join(template_dir,'templates')
#print(template_dir)
app = Flask(__name__, template_folder=template_dir)

@app.route("/")
@app.route("/dashboard")
def home():
    global threadStarted
    if (threadStarted):
        pass
    else:
        threadStarted=True
        #Mqtt
        x = threading.Thread(target=run)
        x.start()

    status = get_robots_status_by_id(1)
    return render_template('dashboard.html', status = status)
   
@app.route("/measurement-history")
def historical():
    return render_template('measurement.html')

@app.route("/event-history")
def events_alarms():
    return render_template('event-history.html')

if __name__ == '__main__':
    app.run(debug=True)
    