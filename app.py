from flask import Flask, request
from FASTory import Workstation
import json
import time

app = Flask(__name__)

history = []
running = True
orders = {}
order_id = 0
workstations = {}
input_file = "fileWithFASTortyinfo"

@app.post("/makeOrder/")
def make_order():
    if request:
        jsonmessage = request.form
        message = json.loads(jsonmessage)
        print(message)
        phone_model = message['phone']
        phone_color = message['color']
        create_order(phone_model,phone_color)

@app.post("/kill/")
def stop():
    global running
    if running:
        running = False
    return True
        
def create_order(model, color):
    global orders
    global order_id
    order = [model, color]
    orders[order_id] = order
    order_id += 1
    
def clear_order(order_id):
    global orders
    del orders[order_id]
    
def move_workstation(ws):
    ws.ready()
    spots = ws.get_spots()
    if spots[2] != -1 and ws.order_ready == False:
        ws.draw(orders[order_id])
    elif spots[4] == -1 and spots[2] != -1:
        suc, msg = ws.move35()
        if not suc:
            print(suc, msg)
    elif spots[2] == -1 and spots[1] != -1:
        suc, msg = ws.move23()
        if not suc:
            print(suc, msg)
    elif spots[1] == -1 and spots[0] != -1:
        suc, msg = ws.move12()
        if not suc:
            print(suc, msg)
    elif spots[3] == -1 and spots[0] != -1:
        suc, msg = ws.move14()
        if not suc:
            print(suc, msg)
    elif spots[4] == -1 and spots[3] != -1:
        suc, msg = ws.move45()
        if not suc:
            print(suc, msg)
    else:
        ws.load_pallet(1,order_id)

def cycle_workstations():
    global workstations
    for ws in workstations:
        move_workstation(ws)
        
def add_workstaion(ws_id, ip_rob, ip_cnv, answerurl, zspot_number):
    global workstations
    ws = Workstation(ws_id, ip_rob, ip_cnv, answerurl, zspot_number)
    workstations.append(ws)
        

if __name__ == '__main__':
    app.run(debug=True, port=8080)
