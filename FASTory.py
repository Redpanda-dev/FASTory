import requests
import socket

#{IP}/_services/{command}
_services = "/rest/services"
_events = "/rest/events/"

class workstation:
    def move12():

        return 0

    def move23():

        return 0

    def move35():

        return 0

    def move14():

        return 0

    def move45():

        return 0
    
    def get_status():
        
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

    return 0
    
main()