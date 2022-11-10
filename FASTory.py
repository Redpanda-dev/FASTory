import requests
import socket

#{IP}/_services/{command}
_services = "/rest/services/"
_events = "/rest/events/"
_ip = socket.gethostbyname(socket.gethostname())

class Workstation:
    def __init__(self,ip_rob, ip_cnv, answerurl, zspot_number):
        self.robot_ip = ip_rob
        self.conveyor_ip = ip_cnv
        self.answerurl = answerurl
        self.roboturl = f'{ip_rob}{_services}'
        self.conveyorurl = f'{ip_cnv}{_events}'
        self.pen_color = None
        self.zspots = [-1]*zspot_number

    def move12(self):
        if self.zspots[0] != -1 and self.zspots[1] == -1:
            body = {"destUrl" : f"{self.answerurl}:8080"}
            response = requests.post(url=f"{self.conveyor_ip}/rest/services/TransZone12", data=body)
            if response.status_code == 202:
                pallet = self.zspots[0]
                self.zspots[1] = pallet
                self.zspots[0] = -1
                return True
        else:
            return False 

    def move23(self):
        if self.zspots[1] != -1 and self.zspots[2] == -1:
            body = {"destUrl" : f"{self.answerurl}:8080"}
            response = requests.post(url=f"{self.conveyor_ip}/rest/services/TransZone23", data=body)
            if response.status_code == 202:
                pallet = self.zspots[1]
                self.zspots[2] = pallet
                self.zspots[1] = -1
                return True
        else:
            return False
        
    def move35(self):
        if self.zspots[2] != -1 and self.zspots[4] == -1:
            body = {"destUrl" : f"{self.answerurl}:8080"}
            response = requests.post(url=f"{self.conveyor_ip}/rest/services/TransZone35", data=body)
            if response.status_code == 202:
                pallet = self.zspots[2]
                self.zspots[4] = pallet
                self.zspots[2] = -1
                return True
        else:
            return False

    def move14(self):
        if self.zspots[0] != -1 and self.zspots[3] == -1:
            body = {"destUrl" : f"{self.answerurl}:8080"}
            response = requests.post(url=f"{self.conveyor_ip}/rest/services/TransZone14", data=body)
            if response.status_code == 202:
                pallet = self.zspots[0]
                self.zspots[3] = pallet
                self.zspots[0] = -1
                return True
        else:
            return False

    def move45(self):
        if self.zspots[3] != -1 and self.zspots[4] == -1:
            body = {"destUrl" : f"{self.answerurl}:8080"}
            response = requests.post(url=f"{self.conveyor_ip}/rest/services/TransZone45", data=body)
            if response.status_code == 202:
                pallet = self.zspots[3]
                self.zspots[3] = pallet
                self.zspots[4] = -1
                return True
        else:
            return False
    
    def load_pallets(self, spot, value):
        self.zspots[spot-1] = value
        

    def get_status(self, spot):
        
        return self.zspots[spot-1]

    def draw(self, receipe):

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
        response = requests.get(url=f"{self.robot_ip}/rest/services/GetPenColor")
        return response.json()
    
    def initialize(self):
        for spot in range(len(self.zspots)):
            self.zspots[spot] = self.get_status(spot+1)
            

def check_IP():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        #print(ipv4) #sanity check ip
        return ip
    except:
        print('Something happened with IP. Dunno lol:D')



def main():
    ip = check_IP()
    print("Currently connected to ", ip)
    station1 = Workstation(ip,5)
    station1.load_pallets(1, "Pallet")
    print(station1.get_status(1))
    station1.move12()
    print(station1.get_status(1))
    print(station1.get_status(2))
    
    return 0
    
main()