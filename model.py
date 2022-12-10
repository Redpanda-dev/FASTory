import paho.mqtt.client as mqtt
import configparser
import os
import random
import json
import sqlite3

######################## HOW TO RUN THE PROGRAM #########################
#                                                                       #
#   In order to run the program you need to install the dependencies    #
#   After dependencies:                                                 #    
#   > Navigate to the programs folder                                   #
#   > Check the configfile and template_dir variables to match the      #
#     folder where they are located                                     #
#   > run: python front.py                                              #
#   > If webpage does not automaticall open:                            #
#   open it manually by navigating to address: http://127.0.0.1:5000/   #
#                                                                       #
#########################################################################

mqtt_topic_name = 11
devId = -1
state = 'Null'
time = 'Null'
status = {'deviceId':devId, 'state': state, 'time':time}
threadStarted=False

###################### STORE DATA (SCADA) ######################

# This is the this
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect(':memory:', check_same_thread=False)
conn.row_factory = dict_factory
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS robot;")
c.execute("""CREATE TABLE IF NOT EXISTS robot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            devId TEXT,
            state TEXT,
            time TIMESTAMP
            );""")

# CREATE A ROBOT -> IF CREATED -> UPDATE
def insert_robot(devId, state, time):
    with conn:
        c.execute("INSERT INTO robot VALUES (:id, :devId, :state, :time)", {'id': None, 'devId': devId, 'state': state, 'time': time})
        #update_robot(rid, devId, state, time)

# READ ROBOTS STATUS BY ID
def get_robots_current_status_by_rid(id):
    c.execute("SELECT devId, state, time FROM robot WHERE devId=:devId", {'devId': id})
    #fetchone = c.fetchone()
    fetchall = c.fetchall()
    print(fetchall)
    i = len(fetchall)
    if i > 0:
        last = fetchall[i-1]
        #print(last)
        return last
    else:
        return []

# READ ALL ROBOTS STATUSES BY ID
def get_robots_all_statuses_by_rid(id):
    c.execute("SELECT devId, state, time FROM robot WHERE devId=:devId", {'devId': id})
    #fetchone = c.fetchone()
    fetchall = c.fetchall()
    i = len(fetchall)
    if i > 0:
        return fetchall
    else:
        return []

# READ ALL ROBOTS STATUSES BY ID
def get_robots_ALL_by_rid_and_state(id, state):
    c.execute("SELECT devId, state, time FROM robot WHERE devId=:devId AND state=:state", {'devId': id, 'state':state})
    fetchall = c.fetchall()
    i = len(fetchall)
    if i > 0:
        return fetchall
    else:
        return []

def get_robots_unique_states_by_rid(id):
    c.execute("""SELECT DISTINCT state FROM robot WHERE devId=:devId""", {'devId': id})
    #fetchone = c.fetchone()
    fetchall = c.fetchall()
    print(fetchall)
    i = len(fetchall)
    if i > 0:
        return fetchall
    else:
        return []

def get_robots_amount_of_of_statues_By_rid_and_status(nID, state):
    c.execute("""
    SELECT 
        state,
        COUNT(*) AS 'amount'
    FROM 
        robot 
    WHERE 
        devId=:devId AND state=:state
    """, {'devId': nID, 'state':state})
    fetch = c.fetchone()
    #print(fetch)
    return fetch

# READ ALL ROBOTS
def get_all_robots():
    #c.execute("SELECT * FROM robot WHERE brand=:brand", {'brand': brand})
    sqlSt="SELECT * FROM robot WHERE 1"
    c.execute(sqlSt)
    #print(c.fetchall())
    return c.fetchall()

# UPDATE ROBOTS VALUES
def update_robot(id, devId, state, time): 
    with conn:
        c.execute("""UPDATE robot 
                    SET devId = :devId, state = :state, time = :time
                    WHERE id = :id""",
                  {'id': id, 'devId': devId,'state':state, 'time':time})

# DELETE A ROBOT FROM LIST
def remove_robot(devId):
    with conn:
        c.execute("""DELETE 
                        from robot
                    WHERE 
                        id = :id""",
                  {'devId': devId})

###################### COMMUNICATION ######################

# GET PATH TO THE CONFIG FILE
# Original Path = C:\Users\Miska\Documents\AUT840\GIT\FASTory\templates
configfile = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
configfile = os.path.join(configfile,'Documents')
configfile = os.path.join(configfile,'FASTory')
configfile = os.path.join(configfile,'config.ini')

config = configparser.ConfigParser()
config.sections()
config.read(configfile)

# CONNECT TO BROKER AND DEFINE CLIENT
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

# SUBSCRIBE TO A TOPIC
def subscribe(client, topic):
    global devId,state,time,status
    def on_message(client, userdata, msg):
        global devId,state,time,status
        #print(f"Received {msg.payload.decode()} from {msg.topic} topic")
        m_in = json.loads(msg.payload.decode()) #decode json data
        #print(m_in)
        devId = m_in['deviceId']
        state = m_in['state']
        time = m_in['time']
        insert_robot(devId, state, time) # ADD ROBOT TO SQL
        #robots = get_robots_state_by_id(1)
        #print(robots['state'])
    client.subscribe(topic)
    client.on_message = on_message

def run():
    DEBUG = 0
    # Check MQTT connection with Mosquitto
    if DEBUG == 1:
        broker = str(config['DEBUG']['mqtt_broker'])
        port = int(config['DEBUG']['mqtt_port'])
        topic = config['DEBUG']['topic']
        client_id = f'python-mqtt-{random.randint(0, 100)}'

    # Use Courses MQTT settings
    else:
        broker = str(config['CONNECTION']['mqtt_broker'])
        port = int(config['CONNECTION']['mqtt_port'])
        client_id = 'Group-AaroLeeviMiska'
        topic = f'ii22/telemetry/{mqtt_topic_name}'

    print(f'Connecting to {broker} : {port}')
    client = connect_mqtt(broker=broker, port=port, client_id=client_id, DEBUG=DEBUG)
    subscribe(client, topic)
    client.loop_forever()  # Start networking daemon