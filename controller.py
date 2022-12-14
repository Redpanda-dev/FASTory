import matplotlib.pyplot as pyplot
import model
import time
import datetime

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

date_format = '%Y-%m-%d %H:%M:%S.%f'

# RETURN HISTORICAL DATA
def historicalData_By_ID(nID):
    diagramData, rationValues = State_rations_By_ID(nID)
    MTBFData = checkMTBF_By_ID(nID)
    return diagramData, rationValues, MTBFData

# CALCULATE THE RATIOS OF ALL DIFFERENT STATES OF THE ROBOT 
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

# CALCULATES THE MTBF
def checkMTBF_By_ID(nID):
    # CHECK BY STATE:
    state = "DOWN"
    down_statuses = model.get_robots_ALL_by_rid_and_state(nID, state)
    statuses = model.get_robots_all_statuses_by_rid(nID)
    # CHECK IF STATUSES EXIST
    if len(statuses) > 0:
        first = datetime.datetime.strptime(statuses[0]['time'], date_format)
        l = len(down_statuses)-1 # GET LAST DOWN STATUS 
        last = datetime.datetime.strptime(statuses[l]['time'], date_format)
        operating_time = last-first
        number_of_failures = len(down_statuses)
        if (number_of_failures) != 0:
            MTBF = (operating_time) / (number_of_failures) # HOW MANY FAILURES DURING OPERATION (= MTBF)
            return MTBF
    else:
        return 0

# RETURN ALARM LOGS
def alarms_By_ID(nID, alertTime):
    idle = alarm_IDLE_state_By_ID(nID, alertTime)
    down = alarm_DOWN_state_By_ID(nID, alertTime)
    return idle, down

# GET ALARMS OF IDLE STATE BY ID AND SPECIFIED ALERTTIME
def alarm_IDLE_state_By_ID(nID, alertTime):
    current_time = datetime.datetime.now() # TIME NOW
    model.update_LOG_of_state_by_ID(nID, "idle")
    statuses = model.get_LOG_of_state_by_ID(nID, "idle")
    #print("Statuses in alarm: ",statuses)
    log = []
    for i in statuses:
        timestamp = i['time'] 
        timeobj = datetime.datetime.strptime(timestamp, date_format)
        time_dif = current_time-timeobj
# GET ALL STATUSES THATS TIME DIFFERENCE IS LARGER THAN ALERTTIME
        if time_dif > datetime.timedelta(minutes=alertTime): 
            log.append(i)
        else:
            pass
    return log

# GET ALARMS OF DOWN STATE BY ID AND SPECIFIED ALERTTIME
def alarm_DOWN_state_By_ID(nID, alertTime):
    current_time = datetime.datetime.now()
    model.update_LOG_of_state_by_ID(nID, "down")
    statuses = model.get_LOG_of_state_by_ID(nID, "down")
    #print("Statuses in alarm: ",statuses)
    log = []
    for i in statuses:
        timestamp = i['time']
        timeobj = datetime.datetime.strptime(timestamp, date_format)
        time_dif = current_time-timeobj
        if time_dif > datetime.timedelta(minutes=alertTime):
            log.append(i)
        else:
            pass
    return log

# DRAW A FIGURE OF STATES BY ID
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
            shadow=False, startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    img = f'static/piechart{nID}.png'
    pyplot.savefig(img)
    return fig
