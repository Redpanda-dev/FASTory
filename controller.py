import matplotlib.pyplot as pyplot
import model
import time

# HISTORICAL DATA
def historicalData_By_ID(nID):
    diagramData, rationValues = State_rations_By_ID(nID)
    MTBFData = checkMTBF_By_ID(nID)
    return diagramData, rationValues, MTBFData

def State_rations_By_ID(nID):
    values = []
    uniqueStates_list = model.get_robots_unique_states_by_rid(nID)
    # Gather amount of each unique state into a list
    for uniqueStates_dicts in uniqueStates_list:
        for j in uniqueStates_dicts:
            state = uniqueStates_dicts[j]
            state_dict = model.get_robots_amount_of_of_statues_By_rid_and_status(nID, state)
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
    statuses = model.get_robots_all_statuses_by_rid(nID)

    pass

# ALARMS
def alarms_By_ID(nID, alertTime):
    idle = alarm_IDLE_state_By_ID(nID, alertTime)
    down = alarm_DOWN_state_By_ID(nID, alertTime)
    return idle, down

def alarm_IDLE_state_By_ID(nID, alertTime):
    current_time = time.time()
    state = 'IDLE'
    statuses = model.get_robots_ALL_by_rid_and_state(nID, state)
    last = len(statuses)-1
    if(last > 0):
        timestamp = statuses[last]['time']
        time_dif = current_time-timestamp
        if time_dif > alertTime:
            return timestamp
        else:
            return {}

def alarm_DOWN_state_By_ID(nID, alertTime):
    current_time = time.time()
    state = 'DOWN'
    statuses = model.get_robots_ALL_by_rid_and_state(nID, state)
    last = len(statuses)-1
    if(last > 0):
        timestamp = statuses[last]['time']
        time_dif = current_time-timestamp
        if time_dif > alertTime:
            return timestamp
        else:
            return {}

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