import paho.mqtt.client as mqtt
from flask import Flask, request as flaskrequest
import requests
import json
import os
import configparser
import threading

# Run this in a differnt instance

mqtt_topic_name = 11
devId = -1
state = 'Null'
time = 'Null'
status = {'deviceId':devId, 'state': state, 'time':time}
threadStarted=False

class Bridge:
    def __init__(self,broker, port, client_id) -> None:
        self.client = self.connect_mqtt(broker, port, client_id)
        self.topic = None

    # CONNECT TO BROKER AND DEFINE CLIENT
    def connect_mqtt(self, broker, port, client_id) -> mqtt:
        print(f'Connecting to {broker} : {port}')
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)
        client = mqtt.Client(client_id)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client

    # SUBSCRIBE TO A TOPIC
    def subscribe_topics(self, topic):
        global devId,state,time,status
        self.topic = topic
        self.client.subscribe(topic)

    def run_mqtt(self, topic):
        self.subscribe_topics(topic)
        x = threading.Thread(target=self.client.loop_forever)
        x.start()
        
    def run_server(self, name):
        app = Flask(name)

        @app.post("/publish/")
        def publish():
            payload = json.loads(flaskrequest.form)
            mqttpayload = json.dumps(payload)
            self.client.publish(topic=self.topic, payload=mqttpayload)
        
        @app.get("/helloworld/")
        def helloworld():
            return "Hello World"
        
        app.run(port=8080)
        
    def subscribe_events(self, host, eventID, destUrl):
        msg = {"destUrl" : f"{destUrl}/publish/"}
        url = f"http://{host}/rest/events/{eventID}/notifs"
        payload = json.dumps(msg)
        response = requests.post(url=url, data=payload)

def run_mqtt_http():
    # GET PATH TO THE CONFIG FILE
    # Original Path = C:\Users\Miska\Documents\AUT840\GIT\FASTory\templates
    configfile = os.path.abspath(os.path.dirname(__file__))
    configfile = os.path.join(configfile,'config.ini')

    config = configparser.ConfigParser()
    config.sections()
    config.read(configfile)

    DEBUG = 0
    # Check MQTT connection with Mosquitto
    if DEBUG == 1:
        broker = str(config['DEBUG']['mqtt_broker'])
        port = int(config['DEBUG']['mqtt_port'])
        topic = config['DEBUG']['topic']
        client_id = f'python-mqtt-{random.randint(0, 100)}'
    # Use Courses MQTT settings
    else:
        broker = str(config['CONNECTION']['mqtt_broker'])
        port = int(config['CONNECTION']['mqtt_port'])
        client_id = 'Group-AaroLeeviMiska'
        topic = f'ii22/telemetry/{mqtt_topic_name}'

    midwear = Bridge(broker, port, client_id)
    midwear.run_mqtt(topic)
    midwear.run_server("midwear")

if __name__ == '__main__':
    run_mqtt_http()
    