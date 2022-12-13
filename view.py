from flask import Flask, render_template, request, Response
import threading
import os
import time as t
import webbrowser
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import model
import controller

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

# GET PATH TO TEMPLATES
# Original Path = C:\Users\Miska\Documents\AUT840\GIT\FASTory\templates
template_dir = os.path.abspath(os.path.dirname(__file__)) # ROOT
template_dir = os.path.join(template_dir,'templates')
#print(template_dir)
app = Flask(__name__, template_folder=template_dir)
webbrowser.open("http://127.0.0.1:5000/dashboard")

threadStarted = model.threadStarted

@app.route("/")
@app.route("/dashboard")
def home():
    global threadStarted

    if (threadStarted):
        pass
    else:
        threadStarted=True
        # Start Mqtt thread
        x = threading.Thread(target=model.run)
        t.sleep(1)
        x.start()

    # Check address -> address needs to be int
    try:
        id = int(request.args.get('nID'))
    except:
        id = 1
    
    nID = f'rob{id}'
    #print(nID)

    status = model.get_robots_current_status_by_rid(nID)
    
    return render_template('dashboard.html', status = status)

@app.route("/measurement-history", methods=['GET', 'POST'])
def historical():
    global threadStarted
    if (threadStarted):
        pass
    else:
        threadStarted=True
        # Start Mqtt thread
        x = threading.Thread(target=model.run)
        t.sleep(1)
        x.start()

    # Check address -> address needs to be int
    try:
        id = int(request.args.get('nID'))
        #print(id)
    except:
        id = 1
    
    nID = f'rob{id}'
    status = model.get_robots_current_status_by_rid(nID)
    rations, rationsValues, mtbf = controller.historicalData_By_ID(nID)
    labels = []
    sizes = []

    for dicts in rations:
        for key in dicts:
            labels.append(key)
            sizes.append(dicts[key])
    
    return render_template('historical-data.html', status = status, len=len(labels), labels = labels, sizes = sizes, values = rationsValues, mtbf = mtbf)

@app.route('/plot.png')
def plot_png():
    try:
        id = int(request.args.get('nID'))
    except:
        id = 1
        
    #print(id)

    nID = f'rob{id}'
    status = model.get_robots_current_status_by_rid(nID)
    #print(status)
    if len(status) > 0:
        global labels, sizes
        fig = controller.create_figure(status['devId'])
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')
    else: 
        output = io.BytesIO()
        return Response(output.getvalue())

@app.route("/event-history")
def events_alarms():
    global threadStarted
    if (threadStarted):
        pass
    else:
        threadStarted=True
        # Start Mqtt thread
        x = threading.Thread(target=model.run)
        t.sleep(1)
        x.start()
    
    # Check address -> address needs to be int
    try:
        id = int(request.args.get('nID'))
    except:
        id = 1

    nID = f'rob{id}'
    model.create_LOG_of_DOWN_by_ID(nID)
    model.create_LOG_of_IDLE_by_ID(nID)

    status = model.get_robots_current_status_by_rid(nID)

    alarm_threshold = 60
    idle, down = controller.alarms_By_ID(nID, alarm_threshold)

    return render_template('event-history.html', status = status, idle = idle, down = down, alarm_threshold = alarm_threshold)

    # START MQTT COMMUNICATION


if __name__ == '__main__':
    app.run(debug=False)