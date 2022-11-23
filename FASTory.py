import requests
import socket
import time
import json

#{IP}/_services/{command}
_ip = socket.gethostbyname(socket.gethostname())
TEST = True


class Workstation:
    def __init__(self, ws_id, ip_rob, ip_cnv, answerurl, zspot_number):
        self.id = ws_id
        self.robot_ip = f"http://{ip_rob}"
        self.conveyor_ip = f"http://{ip_cnv}"
        self.answerurl = f"http://{answerurl}:8080"
        self.pen_color = None
        self.zspots = [-1]*zspot_number     # -1 means the spot is empty
        self.busy = False
        self.order_ready = False
        self.responses = {
            1 : "Success",
            2 : "Wrong status response",
            3 : "Conveyor is busy or spot is occupied",
            4 : "Connection problem: "
        }

    def move12(self):
        if self.busy == False and self.zspots[0] != -1 and self.zspots[1] == -1:
            body = '{"destUrl" : ""}'
            try:
                response = requests.post(url=f"{self.conveyor_ip}/rest/services/TransZone12", data=body, timeout=1)
                if response.status_code == 202:
                    self.busy = True
                    self.__move_pallet(1,2)
                    return (True, self.responses[1])
                return (False, self.responses[2])
            except requests.exceptions.RequestException as e:
                return (False, self.responses[4])
        else:
            return  (False, self.responses[3])

    def move23(self):
        if self.busy == False and self.zspots[1] != -1 and self.zspots[2] == -1:
            body = '{"destUrl" : ""}'
            try:
                response = requests.post(url=f"{self.conveyor_ip}/rest/services/TransZone23", data=body, timeout=1)
                if response.status_code == 202:
                    self.busy = True
                    self.__move_pallet(2,3)
                    return (True, self.responses[1])
                return (False, self.responses[2])
            except requests.exceptions.RequestException as e:
                return (False, self.responses[4])
        else:
            return  (False, self.responses[3])
        
    def move35(self):
        if self.busy == False and self.zspots[2] != -1 and self.zspots[4] == -1:
            body = '{"destUrl" : ""}'
            try:
                response = requests.post(url=f"{self.conveyor_ip}/rest/services/TransZone35", data=body, timeout=1)
                if response.status_code == 202:
                    self.busy = True
                    self.__move_pallet(3,5)
                    return (True, self.responses[1])
                return (False, self.responses[2])
            except requests.exceptions.RequestException as e:
                return (False, self.responses[4])
        else:
            return  (False,self.responses[3])

    def move14(self):
        if self.busy == False and self.zspots[0] != -1 and self.zspots[3] == -1:
            body = '{"destUrl" : ""}'
            try:
                response = requests.post(url=f"{self.conveyor_ip}/rest/services/TransZone14", data=body, timeout=1)
                if response.status_code == 202:
                    self.busy = True
                    self.__move_pallet(1,4)
                    return (True, self.responses[1])
                return (False, self.responses[2])
            except requests.exceptions.RequestException as e:
                return (False, self.responses[4])
        else:
            return  (False,self.responses[3])

    def move45(self):
        if self.busy == False and self.zspots[3] != -1 and self.zspots[4] == -1:
            body = '{"destUrl" : ""}'
            try:
                response = requests.post(url=f"{self.conveyor_ip}/rest/services/TransZone45", data=body, timeout=1)
                if response.status_code == 202:
                    self.busy = True
                    self.__move_pallet(4,5)
                    return (True, self.responses[1])
                return (False, self.responses[2])
            except requests.exceptions.RequestException as e:
                return (False, self.responses[4])
        else:
            return  (False,self.responses[3])
    
    def load_pallets(self, spot, value):
        self.zspots[spot-1] = value
        

    def get_status(self, spot):
        try:
            response = requests.post(url=f"{self.conveyor_ip}/rest/services/Z{spot}", data='{}' )
            res = json.loads(response.text)
            return res["PalletID"]
        except requests.exceptions.RequestException as e:
            return (False, self.responses[4])

    def draw(self, receipe):
        self.order_ready = True
        self.busy = True
        return 0
    
    # r="RED", g="GREEN", b="BLUE"
    def select_pen(self, c):
        if c == "r" or c == "RED":
            s = "ChangePenRED"
        elif c == "g" or c == "GREEN":
            s = "ChangePenGREEN"
        elif c == "b" or c == "BLUE":
            s = "ChangePenBLUE"
        else:
            print("Undefined color")

        command = f'{self.robot_ip}/rest/services/{s}'
        response = requests.post(url=command)
        if response.status_code == 202:
            self.pen_color = "RED"
            
    def get_pen_color(self):
        try:
            response = requests.get(url=f"{self.robot_ip}/rest/services/GetPenColor")
            return response.json()
        except requests.exceptions.RequestException as e:
            return (False, self.responses[4])
    
    def initialize(self):
        for spot in range(len(self.zspots)):
            self.zspots[spot] = self.get_status(spot+1)
            
    def ready(self):
        self.busy = False
        
    def __move_pallet(self,spot1, target):
        self.zspots[target-1] = self.zspots[spot1-1]
        self.zspots[spot1-1] = -1
        
    def get_spots(self):
        return self.zspots


def check_IP():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        #print(ipv4) #sanity check ip
        return ip
    except:
        print('Something happened with IP. Dunno lol:D')
        
def viasualize(ws):
    visu = f"   /--[{ws.zspots[3]:3}]----------\\   \n-[{ws.zspots[4]:3}]----[{ws.zspots[2]:3}]-[{ws.zspots[1]:3}]---[{ws.zspots[0]:3}]"
    print(visu)
    print()


def main():
    print("Test script")
    
    print("Create WS")
    ws = Workstation("10", "192.168.10.1", "192.168.10.2", "127.0.0.1",5)
    
    print("Initialize WS")
    # ws.initialize()
    print("WS spot pallet ids:")
    viasualize(ws)
    
    if -1 in ws.zspots:
        print("Cnv empty, load pallets")
        ws.load_pallets(1,"1")
        ws.load_pallets(2,"2")
        print()
        viasualize(ws)
        
    print("move 12")
    suc, msg = ws.move12()
    print(msg)
    viasualize(ws)
    
    print("move 23")
    suc, msg = ws.move23()
    print(msg)
    viasualize(ws)
    
    print("move 14")
    suc, msg = ws.move14()
    print(msg)
    viasualize(ws)
    
    print("toggle ws")
    ws.ready()
    
    print("move 14")
    suc, msg = ws.move14()
    print(msg)
    viasualize(ws)
    
    print("move 12")
    suc, msg = ws.move35()
    print(msg)
    viasualize(ws)
    
    print("move 45")
    suc, msg = ws.move45()
    print(msg)
    viasualize(ws)
    

if __name__ == '__main__':
    main()
    