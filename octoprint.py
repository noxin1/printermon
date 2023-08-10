import urllib.request
import json
import subprocess
import time
import serial
import sys
import random
import re
import string
import signal
import configparser

curcolor = ""
HEXCODE=b"#000000\n"

def loadconfig():
    config = configparser.ConfigParser()
    global printerip
    global usbled
    global apikey
    try:
      config.read('printers.led')
    except Exception as e:
      print("Config file - unabled to load printers.led", e)
      exit(1)
    else:
      printerip = config[printer]['ip']
      usbled = config[printer]['usbled']
      apikey = config[printer]['apikey']
      #print(printerip, usbled)

def setcolor(color):
    global curcolor
    global usbled
    #print(color)
    if curcolor != color:
      timeout= time.strftime("%Y-%m-%D %H:%M:%S")
      print(f"{timeout} {printer} New Color", curcolor, color)
      if color == "white":
        HEXCODE=b"#FFFFFF\n"
      elif color == "yellow":
        HEXCODE=b"#121200\n"
      elif color == "purple":
        HEXCODE=b"#990099\n"
      elif color == "green":
        HEXCODE=b"#000500\n"
      elif color == "red":
        HEXCODE=b"#250000\n"
      elif color == "blue":
        HEXCODE=b"#000025\n"
      elif color == "black":
        HEXCODE=b"#000000\n"
      elif color == "slowg":
        HEXCODE=b"B#001100-1000#000000-6000\n"
      cmd = f"ls /dev/serial/by-id/{usbled}"
      OUTP = subprocess.getoutput(cmd)
    #print(OUTP)
      ser = serial.Serial(OUTP)
      ser.write(HEXCODE)
      ser.close()
    #else:
    #  print("Nothing to do here")

    curcolor=color

def processmsg():
     output = urllib.request.urlopen(f"http://{printerip}/api/printer?apikey={apikey}").read()
     data = json.loads(output)
     #print(data)
     try:
         stage = data['state']['flags']['operational']
     except Exception as e:
         timeout= time.strftime("%Y-%m-%D %H:%M:%S")
         print(f"{timeout} {printer} Stage Check Failed")
         time.sleep(2)
         return()
#         print("No Webhooks Entry")
#     else:
#         #/print("Stage is ", stage)
#         if not stage:
#             setcolor("red")
#             time.sleep(2)
#             return()
     try:
         printstats = data['state']['flags']
     except Exception as e:
          print("No print_stats Entry")
     else:
         #print(printstats)
         if printstats['paused'] or printstats['pausing']:
             setcolor("purple")
         elif printstats['error'] or printstats['closedOrError']:
             setcolor("red")
         elif printstats['cancelling']:
             setcolor("yellow")
         elif printstats['finishing'] or printstats['printing'] or printstats['resuming']:
             setcolor("green")
         elif printstats['operational']:
             setcolor("slowg")
         else:
             setcolor("black")
     time.sleep(2)

def sigterm_handler(_signo, _stack_frame):
    sys.exit(0)

def run():
    global printer
    signal.signal(signal.SIGTERM, sigterm_handler)
    try:
        printer = sys.argv[1]
    except IndexError:
        print("Please enter a printer to monitor")
        exit(1)
    loadconfig()
    setcolor("white")
    try:
      while True:
        try:
          processmsg()
        except KeyboardInterrupt:
          setcolor("black")
          exit()
        except Exception as e:
          print("Uhoh", e)
          setcolor("yellow")
          time.sleep(30)
    finally:
      setcolor("black")

if __name__ == '__main__':
    run()

