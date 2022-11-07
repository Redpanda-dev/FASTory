import requests
import socket

#{IP}/_services/{command}
_services = "/rest/services/"
_events = "/rest/events/"
_ip = socket.gethostbyname(socket.gethostname())

class Workstation:
    def __init__(self,ip):
        self.serviceurl = f'{ip}{_services}'
        self.eventsurl = f'{ip}{_events}'

    def move12(self):

        return 0

    def move23(self):

        return 0

    def move35(self):

        return 0

    def move14(self):

        return 0

    def move45(self):

        return 0
    
    def get_status(self):

        return 0

    def draw(self, receipe):

        return 0
    
    #r="RED", g="GREEN", b="BLUE"
    def select_pen(self, c):
        if c == "r" or c == "RED":
            s = "ChangePenRED"
        elif c == "g" or c == "GREEN":
            s = "ChangePenGREEN"
        elif c == "b" or c == "BLUE":
            s = "ChangePenBLUE"
        else:
            print("Undefined color")

        command = f'{self.serviceurl}{s}'
        requests.post(url=command)
        return 0

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
    Workstation(ip).select_pen("r")
    return 0
    
main()