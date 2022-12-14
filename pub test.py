import paho.mqtt.client as mqtt
import configparser
import os
import time

configfile = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
configfile = os.path.join(configfile,'GIT')
configfile = os.path.join(configfile,'FASTory')
configfile = os.path.join(configfile,'config.ini')

config = configparser.ConfigParser()
config.sections()
config.read(configfile)


# Replace the following with the appropriate values for your MQTT server
MQTT_BROKER = str(config['DEBUG']['mqtt_broker'])
MQTT_PORT = int(config['DEBUG']['mqtt_port'])

# Replace "topic" with the name of the topic you want to publish to,
# and "message" with the message you want to send
MQTT_TOPIC = "ii22/telemetry/11"
MQTT_MESSAGE = """{
"deviceId":"rob1",
"state":"READY",
"time": "2022-11-09 16:00:00.0"
}"""

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# Create an MQTT client instance
client = mqtt.Client()

# Attach the callback function to the "on_connect" event
client.on_connect = on_connect

# Connect to the MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT)

# Start the MQTT client loop to allow for publishing
client.loop_start()

# Publish the message continuously at 1-second intervals
while True:
    client.publish(MQTT_TOPIC, MQTT_MESSAGE)
    time.sleep(1)