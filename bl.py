
# python3.6

import random
import ssl
import json
import sys
import serial
import time
import subprocess
import re
import string
import signal
import configparser
from os.path import exists
from paho.mqtt import client as mqtt_client

port = 8883
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = "bblp"
curcolor = ""

def loadconfig():
    config = configparser.ConfigParser()
    global broker
    global serialnumber
    global password
    global usbled
    try:
      config.read('printers.led')
    except Exception as e:
      print("Config file - unabled to load printers.led", e)
      exit(1)
    else:
      broker = config[printer]['ip']
      serialnumber = config[printer]['serialnumber']
      password = config[printer]['accesscode']
      usbled = config[printer]['usbled']

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc != 0:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def setcolor(color):
    global curcolor
    global usbled
    #print(color)
    if curcolor != color:
      timeout= time.strftime("%Y-%m-%D %H:%M:%S")
      print(f"{timeout} {printer} New Color", curcolor, color)
      if color == "white":
        HEXCODE=b"B#050505\n"
      elif color == "yellow":
        HEXCODE=b"B#050500\n"
      elif color == "purple":
        HEXCODE=b"B#050005\n"
      elif color == "green":
        HEXCODE=b"B#000500\n"
      elif color == "red":
        HEXCODE=b"B#050000\n"
      elif color == "blue":
        HEXCODE=b"B#000005\n"
      elif color == "black":
        HEXCODE=b"B#000000\n"
      elif color == "slowgreen":
        HEXCODE=b"B#000500-1000#000000-6000\n"
      elif color == "slowyellow":
        HEXCODE=b"B#414410-1000#000000-6000\n"
      elif color == "fastred":
        HEXCODE=b"B#300000-0500#000000-1000\n"
      cmd = f"ls /dev/serial/by-id/{usbled}"
      OUTP = subprocess.getoutput(cmd)
    #print(OUTP)
      ser = serial.Serial(OUTP)
      ser.write(HEXCODE)
      ser.close()
    #else:
    #  print("Nothing to do here")

    curcolor=color
    
def publish(client):
    global serialnumber
    topicpublish = f"device/{serialnumber}/request"
    msg ='''{ "pushing": { "sequence_id": "888888888", "command": "pushall" } }'''
    result = client.publish(topicpublish, msg, qos=0, retain=True)
    # result: [0,1]
    status = result[0]
    #if status == 0:
    #   print(f"Send `{msg}` to topic `{topicpublish}`")
    #else:
    #   print(f"Failed to send message to topic {topicpublish}")
    #print(status)

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        #print(f"`{msg.payload.decode()}`")
        printer_data=json.loads(msg.payload.decode())
        try:
           stage = printer_data['print']['stg_cur']
        except Exception as e:
           #print("No Status Message Found")
           #print(msg.payload.decode())
           blah = "blah"
        else:
           if stage == 6 or stage == 17 or stage == 20 or stage == 21:
              setcolor("red")
           elif stage == 5 or stage == 16:
               setcolor("yellow")
           elif stage == 4:
               setcolor("slowyellow")
           elif stage == -1:
              setcolor("slowgreen")
           elif stage == 14:
              setcolor("black")
           elif stage == 255:
               setcolor("slowgreen")
           else:
              setcolor("green")


    topic = f"device/{serialnumber}/report"
    client.subscribe(topic)
    if curcolor == "white":
        timeout= time.strftime("%Y-%m-%D %H:%M:%S")
        print(f"{timeout} {printer} Unknown Status, sending a message to the request topic")
        setcolor("red")
        publish(client)
    client.on_message = on_message

def sigterm_handler(_signo, _stack_frame):
    sys.exit(0)

def run():
    global printer
    signal.signal(signal.SIGTERM, sigterm_handler)
    try:
        printer = sys.argv[1]
    except IndexError:
        print("Please Enter a printer to monitor")
        exit(1)
    loadconfig()
    setcolor("white")
    time.sleep(2)
    client = connect_mqtt()
    subscribe(client)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        setcolor("black")
        exit()
    except Exception as e:
        blah = "blah"
    finally:
        setcolor("black")

if __name__ == '__main__':
    run()

