from flask import Flask, render_template, request, Response
import threading
import paho.mqtt.client as mqtt
import configparser
import os
import random
import time as t
import json
import sqlite3
import webbrowser
import io
import matplotlib.pyplot as pyplot
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

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

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect(':memory:',check_same_thread=False)
conn.row_factory = dict_factory
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS robot;")
c.execute("""CREATE TABLE IF NOT EXISTS robot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            devId text,
            state text,
            time text
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

###################### PROCESS DATA ######################

# HISTORICAL DATA
def historicalData_By_ID(nID):
    diagramData = State_rations_By_ID(nID)
    MTBFData = checkMTBF_By_ID(nID)
    return diagramData, MTBFData

def State_rations_By_ID(nID):
    values = []
    uniqueStates_list = get_robots_unique_states_by_rid(nID)
    # Gather amount of each unique state into a list
    for uniqueStates_dicts in uniqueStates_list:
        for j in uniqueStates_dicts:
            state = uniqueStates_dicts[j]
            state_dict = get_robots_amount_of_of_statues_By_rid_and_status(nID, state)
            values.append(state_dict)
    
    # Sum of all states
    sum = 0
    for dicts in values:
        sum += dicts['amount']
    
    # Ratio of each state
    rations = []
    for dicts in values:
        temp = {}
        r = (dicts['amount'] / sum)*100
        temp[dicts['state']] = r
        rations.append(temp)

    return rations, values

def checkMTBF_By_ID(nID):
    statuses = get_robots_all_statuses_by_rid(nID)

    pass

# ALARMS
def alarms_By_ID(nID):
    idle = alarm_IDLE_state_By_ID(nID)
    down = alarm_DOWN_state_By_ID(nID)
    return idle, down

def alarm_IDLE_state_By_ID(nID):
    statuses = get_robots_all_statuses_by_rid(nID)
    pass
def alarm_DOWN_state_By_ID(nID):
    statuses = get_robots_all_statuses_by_rid(nID)
    pass

def draw_Pie_plot(nID):
    rations = State_rations_By_ID(nID)



###################### COMMUNICATION ######################

# GET PATH TO THE CONFIG FILE
# Original Path = C:\Users\Miska\Documents\AUT840\GIT\FASTory\templates
configfile = os.path.abspath(os.path.dirname(__file__))
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

# START MQTT COMMUNICATION
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


###################### APP ######################

# GET PATH TO TEMPLATES
# Original Path = C:\Users\Miska\Documents\AUT840\GIT\FASTory\templates
template_dir = os.path.abspath(os.path.dirname(__file__)) # ROOT
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
        # Start Mqtt thread
        x = threading.Thread(target=run)
        t.sleep(1)
        x.start()

    # Check address -> address needs to be int
    try:
        id = int(request.args.get('nID'))
    except:
        id = 1
    
    nID = f'rob{id}'
    #print(nID)

    status = get_robots_current_status_by_rid(nID)
    
    return render_template('dashboard.html', status = status)

@app.route("/measurement-history", methods=['GET', 'POST'])
def historical():
    global threadStarted
    if (threadStarted):
        pass
    else:
        threadStarted=True
        # Start Mqtt thread
        x = threading.Thread(target=run)
        t.sleep(1)
        x.start()

    # Check address -> address needs to be int
    try:
        id = int(request.args.get('nID'))
        print(id)
    except:
        id = 1
    
    nID = f'rob{id}'
    status = get_robots_current_status_by_rid(nID)
    rations, values = State_rations_By_ID(nID)
    labels = []
    sizes = []

    for dicts in rations:
        for key in dicts:
            labels.append(key)
            sizes.append(dicts[key])
    
    return render_template('historical-data.html', status = status, len=len(labels), labels = labels, sizes = sizes, values = values)

@app.route('/plot.png')
def plot_png():
    try:
        id = int(request.args.get('nID'))
    except:
        id = 1
        
    print(id)

    nID = f'rob{id}'
    status = get_robots_current_status_by_rid(nID)
    print(status)
    if len(status) > 0:
        global labels, sizes
        fig = create_figure(status['devId'])
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')
    else: 
        output = io.BytesIO()
        return Response(output.getvalue())

def create_figure(nID):
    rations, values = State_rations_By_ID(nID)
    labels = []
    sizes = []

    for dicts in rations:
        for key in dicts:
            labels.append(key)
            sizes.append(dicts[key])

    fig, ax = pyplot.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    img = f'static/piechart{nID}.png'
    pyplot.savefig(img)
    return fig

@app.route("/event-history")
def events_alarms():
    global threadStarted
    if (threadStarted):
        pass
    else:
        threadStarted=True
        # Start Mqtt thread
        x = threading.Thread(target=run)
        t.sleep(1)
        x.start()
    
    # Check address -> address needs to be int
    try:
        id = int(request.args.get('nID'))
    except:
        id = 1
    
    nID = f'rob{id}'
    idle, down = alarms_By_ID(nID)
    status = get_robots_current_status_by_rid(nID)

    return render_template('event-history.html', status = status)


webbrowser.open("http://127.0.0.1:5000/dashboard")
if __name__ == '__main__':
    app.run(debug=True)
    
    