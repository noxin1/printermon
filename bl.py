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
import requests
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

def setcolor(color,message):
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
        HEXCODE=b"B#002500\n"
      elif color == "red":
        HEXCODE=b"B#050000\n"
      elif color == "blue":
        HEXCODE=b"B#000005\n"
      elif color == "black":
        HEXCODE=b"B#000000\n"
      elif color == "lowgreen":
        HEXCODE=b"B#000200-1000\n"
      elif color == "slowgreen":
        HEXCODE=b"B#001500-1000#000500-6000\n"
      elif color == "slowyellow":
        HEXCODE=b"B#414410-1000#000000-6000\n"
      elif color == "fastred":
        HEXCODE=b"B#300000-0500#000000-1000\n"
      ###cmd = f"ls /dev/serial/by-id/{usbled}"
      ###OUTP = subprocess.getoutput(cmd)
      OUTP = usbled
    #print(OUTP)
      ser = serial.Serial(OUTP)
      ser.write(HEXCODE)
      ser.close()
      discord(f'{printer} {color} {message}')
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
           #print(stage)
           if stage == 0:
              setcolor("slowgreen", 'Printing')
           elif stage == 1:
               setcolor("slowgreen", 'auto_bed_leveling')
           elif stage == 2:
               setcolor("slowgreen", 'heatbed_preheating')
           elif stage == 3:
               setcolor("slowgreen", 'sweeping_xy_mech_mode')
           elif stage == 4:
               setcolor("slowgreen", 'changing filament')
           elif stage == 5:
               setcolor("slowgreen", 'm400_pause')
           elif stage == 6:
               setcolor("yellow",'paused_filament_runout')
           elif stage == 7:
               setcolor("slowgreen",'heating_hotend')
           elif stage == 8:
               setcolor("slowgreen",'calibrating_extrusion')
           elif stage == 9:
               setcolor("slowgreen",'scanning_bed_surface')
           elif stage == 10:
               setcolor("slowgreen",'inspecting_first_layer')
           elif stage == 11:
               setcolor("slowgreen",'identifying_build_plate_type')
           elif stage == 12:
               setcolor("slowgreen",'calibrating_micro_lidar')
           elif stage == 13:
               setcolor("slowgreen",'homing_toolhead')
           elif stage == 14:
               setcolor("slowgreen",'cleaning_nozzle_tip')
           elif stage == 15:
               setcolor("slowgreen",'checking_extruder_temperature')
           elif stage == 16:
               setcolor("yellow",'paused_user')
           elif stage == 17:
               setcolor("red",'paused_front_cover_falling')
           elif stage == 18:
               setcolor("slowgreen",'calibration_micro_lidar')
           elif stage == 19:
               setcolor("slowgreen",'calibration_extrusion_flow')
           elif stage == 20:
               setcolor("red",'paused_nozzle_temperature_malfunction')
           elif stage == 21:
               setcolor("red",'paused_heat_bed_temperature_malfunction')
           elif stage == 22:
               setcolor("slowyellow",'filament_unloading')
           elif stage == 23:
               setcolor("red",'paused_skipped_step')
           elif stage == 24:
               setcolor("slowyellow",'filament_loading')
           elif stage == 25:
               setcolor("slowgreen",'calibrating_motor_noise')
           elif stage == 26:
               setcolor("red",'paused_ams_lost')
           elif stage == 27:
               setcolor("red",'paused_low_fan_speed_heat_break')
           elif stage == 28:
               setcolor("red",'paused_champer_temperature_control_error')
           elif stage == 29:
               setcolor("slowgreen",'cooling_chamber')
           elif stage == 30:
               setcolor("slowyellow",'paused_user_gcode')
           elif stage == 31:
               setcolor("slowgreen",'motor_noise_showoff')
           elif stage == 32:
               setcolor("red",'paused_nozzle_filament_covered_detected')
           elif stage == 33:
               setcolor("red",'paused_cutter_error')
           elif stage == 34:
               setcolor("red",'paused_first_layer_error')
           elif stage == 35:
               setcolor("red",'paused_nozzle_clog')
           elif stage == 255:
               setcolor("green",'idle/done')
           elif stage == -1:
               setcolor("green",'idle/done')
           else:
               setcolor("Red",'unknown code')


    topic = f"device/{serialnumber}/report"
    client.subscribe(topic)
    if curcolor == "white":
        timeout= time.strftime("%Y-%m-%D %H:%M:%S")
        print(f"{timeout} {printer} Unknown Status, sending a message to the request topic")
        setcolor("red", "Error connecting to printer")
        publish(client)
    client.on_message = on_message

def sigterm_handler(_signo, _stack_frame):
    sys.exit(0)

def discord(MESSAGE):
    WHURL="WEBHOOKURL"
    data = { "content" : MESSAGE, "username" : "Printmon" }
    result = requests.post(WHURL, json = data)
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
#    else:
#        print(f"Payload delivered successfully, code {result.status_code}.")

def run():
    global printer
    signal.signal(signal.SIGTERM, sigterm_handler)
    try:
        printer = sys.argv[1]
    except IndexError:
        print("Please Enter a printer to monitor")
        exit(1)
    loadconfig()
    setcolor("white", "Script Starting")
    time.sleep(2)
    client = connect_mqtt()
    subscribe(client)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        setcolor("black", "Script Shutting Down")
        exit()
    except Exception as e:
        blah = "blah"
    finally:
        setcolor("black", "Script shutting Down")

if __name__ == '__main__':
    run()
