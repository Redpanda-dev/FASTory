import configparser
import os
import random
import sqlite3
from mqtthttp import Bridge

######################## HOW TO RUN THE PROGRAM #########################
#                                                                       #
#   In order to run the program you need to install the dependencies    #
#   After dependencies:                                                 #    
#   > Navigate to the programs folder                                   #
#   > Check the configfile and template_dir variables to match the      #
#     folder where they are located                                     #
#   > run on terminal: python view.py                                   #
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
    with conn:
        c.execute("SELECT devId, state, time FROM robot WHERE devId=:devId", {'devId': id})
        #fetchone = c.fetchone()
        fetchall = c.fetchall()
        #print(fetchall)
        i = len(fetchall)
        if i > 0:
            last = fetchall[i-1]
            #print(last)
            return last
        else:
            return []

# READ ALL ROBOTS STATUSES BY ID
def get_robots_all_statuses_by_rid(id):
    with conn:
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
    with conn:
        c.execute("SELECT devId, state, time FROM robot WHERE devId=:devId AND state=:state", {'devId': id, 'state':state})
        fetchall = c.fetchall()
        i = len(fetchall)
        if i > 0:
            return fetchall
        else:
            return []

def create_LOG_of_IDLE_by_ID(id):
    state = "idle"
    sqlstate = f"""CREATE TABLE IF NOT EXISTS {state}_log_{id} (
        state TEXT,
        time TIMESTAMP);"""
    with conn:
        c.execute(sqlstate)
        update_LOG_of_state_by_ID(id, state)


def create_LOG_of_DOWN_by_ID(id):
    state = "down"
    sqlstate = f"""CREATE TABLE IF NOT EXISTS {state}_log_{id} (
        state TEXT,
        time TIMESTAMP);"""
    with conn:
        if c.execute(sqlstate):
            c.execute(sqlstate)
            update_LOG_of_state_by_ID(id, state)
        else:
            pass
    

def update_LOG_of_state_by_ID(id, state):
    state_upper = state.upper()
    c.execute("""SELECT * FROM robot WHERE devId=:devId AND state=:state""",{'devId': id, 'state':state_upper})
    sqlstate = f"""INSERT INTO {state}_log_{id} SELECT state, time FROM robot WHERE devId=? AND state=?"""
    values = (id, str(state_upper))
    #print(sqlstate, values)
    sqlstate2 = f"SELECT * FROM {state}_log_{id}"
    if c.execute(sqlstate2):
        c.execute(sqlstate, values)
        #print(c.fetchone())
    else:
        pass

def get_LOG_of_state_by_ID(id, state):
    sqlstate = f"""SELECT * FROM {state}_log_{id}"""
    if c.execute(sqlstate):
        c.execute(sqlstate)
        fetchall = c.fetchall()
        return fetchall
    else:
        print(f"Table: {state}_log_{id} does not exist")
        return []
    

def get_robots_unique_states_by_rid(id):
    c.execute("""SELECT DISTINCT state FROM robot WHERE devId=:devId""", {'devId': id})
    fetchall = c.fetchall()
    #print(fetchall)
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