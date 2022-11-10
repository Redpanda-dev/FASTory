from flask import Flask, request
from FASTory import Workstation
import json

app = Flask(__name__)

history = []
orders = {}
order_id = 0
workstations = {}
input_file = "fileWithFASTortyinfo"

@app.post("/makeOrder/")
def make_order():
    global history
    if request:
        jsonmessage = request.form
        message = json.loads(jsonmessage)
        print(message)
        phone_model = message['phone']
        phone_color = message['color']
        history.append(message)
        create_order()
        move_workstations()

@app.post("/actionDone/<ws_id>")
def make_ready(ws_id=None):
    wsid = ws_id
    ws = workstations[wsid]
    ws.ready_for_action()
    move_workstations()
    return 202
    
def FASTory_intialize(input_file):
    with open(input_file, "w") as file:
        data = json.loads(file)
    for ws in data:
        wstation = Workstation(ws['id'], ws['robot']['ip'], ws['conveyor']['ip'], ws['response']['url'], len(ws['spots']))
        wstation.initialize()
        workstations[ws['id']] = wstation
        
def create_order(model, color):
    global orders
    global order_id
    order = [model, color]
    orders[order_id] = order
    order_id += 1
    
def clear_order(order_id):
    global orders
    del orders[order_id]

def move_workstations():
    global workstations
    for ws in workstations:
        ws_status = ws.zspots
        
