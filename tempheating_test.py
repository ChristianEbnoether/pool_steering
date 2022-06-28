#!/usr/bin/python3

import datetime
import RPi.GPIO as GPIO
import time
import os
import glob
import argparse
import time
import sys
from influxdb import InfluxDBClient
import subprocess

#
# Relaisboard/gpio
###################

contact1_gpio = 1 # 
contact2_gpio = 2 # 
contact3_gpio = 3 #
contact4_gpio = 4 # 
5_gpio = 5 #waterfühler

host = '192.168.1.10'
port = 8086
user = []
password = []
dbname= 'water'
session='pool'


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

GPIO.setmode(GPIO.BCM) 
GPIO.setwarnings(False)

count_work=0

#print(count_work)
def get_temp():
    global count_work


    for t in range(1):
        tempfile_Vorlauf = open(Vorlauf)
        text_Vorlauf = tempfile_Vorlauf.read()
        tempfile_Vorlauf.close() 
        tline_Vorlauf = text_Vorlauf.split("\n")[1] # the second line contains temperature
        tdata_Vorlauf = tline_Vorlauf.split(" ")[9] # position 9 contains temparature value
        temp_Vorlauf  += float(tdata_Vorlauf[2:])/1000
   

        if (temp_Dach-temp_Vorlauf > temp_Soll):
            print(temp_Dach)
            print("heating")
            print (temp_Delta)
            GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
            GPIO.setwarnings(False)
            RELAIS_1_GPIO = 16
            GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Assign mode
            GPIO.setup(20, GPIO.OUT) # GPIO Assign mode
            GPIO.setup(21, GPIO.OUT) # GPIO Assign mode
            GPIO.setup(16, GPIO.OUT) # GPIO Assign mode
            #GPIO.output(12, GPIO.LOW) # out
            GPIO.output(20, GPIO.HIGH)
            GPIO.output(21, GPIO.HIGH)
            GPIO.output(12, GPIO.HIGH)
            GPIO.output(16, GPIO.HIGH)
            count_work +=1

    
        if (temp_Dach-temp_Vorlauf < temp_Soll):
            print("waiting")
            GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
            GPIO.setwarnings(False)
            RELAIS_1_GPIO = 16
            GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Assign mode
            GPIO.output(RELAIS_1_GPIO, GPIO.HIGH) # out
            count_dont +=1
    


        else:
            print('out')     
            print(temp_Dach)
            print(temp_Vorlauf)
            print(temp_Dach-temp_Vorlauf) 

        timestamp=datetime.datetime.utcnow().isoformat()
        print(timestamp)
        datapoints = [
            {
                "measurement": session,
                "time": timestamp,
                "fields": {"temp_Dach":temp_Dach,"temp_Vorlauf":temp_Vorlauf,"temp_Nachlauf":temp_Nachlauf,"temp_Luft":temp_Luft,"temp_Delta":temp_Delta,"count_work":count_work,"count_dont":count_dont}
            }

            ]
        return datapoints
    


    else: 
        return (temp_Dach / 1000)

client = InfluxDBClient(host, port, user, password, dbname)

def clear_counter():
    today = datetime.date.today()
    now=(round(time.time() - time.mktime(today.timetuple())))
    if now> 86200 :
        global count_work
        global count_dont
        count_work=0
        count_dont=0
        print(now)



while True:
    datapoints=get_temp()
    bResult=client.write_points(datapoints)
    if GPIO.input(10) == GPIO.HIGH:
        print("Button was pushed!")

    if GPIO.input(10) == GPIO.HIGH:
        print("Button was pushed!")

    else:
        print("else")

    #time.sleep(10)
#    clear_counter()
    print("afterwrite")
    # Create Influxdb datapoints (using lineprotocol as of Influxdb >1.1)
#    print("Write points {0} bResult:{0}".format(datapoints,bResult))
# Initialize the Influxdb client

#        # Write datapoints to InfluxDB
print(count_work)
#print(count_dont)

