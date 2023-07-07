
#!/usr/bin/python3
from datetime import datetime
import RPi.GPIO as GPIO
import time
import os
import glob
import argparse
import time
import datetime
import sys
from influxdb import InfluxDBClient
import RPi.GPIO as GPIO
import subprocess



PUMP_gpio = 21
LAMP_gpio = 20
contact1_gpio = 16
contact2_gpio = 12
dev_path = '/sys/bus/w1/devices/'
dev_Dach = glob.glob(dev_path + '28-0316611d8bff')[0]
dev_Vorlauf = glob.glob(dev_path + '28-031660882fff')[0]
dev_Nachlauf = glob.glob(dev_path + '28-04166127baff')[0]
dev_Luft = glob.glob(dev_path + '28-031660c2f9ff')[0]
Luft = dev_Luft + '/w1_slave'
Dach = dev_Dach + '/w1_slave'
Vorlauf = dev_Vorlauf + '/w1_slave'
Nachlauf = dev_Nachlauf + '/w1_slave'
host = '192.168.100.9'
port = 8086
user = [user]
password = [password]
dbname= 'water'
session='pool'


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

GPIO.setmode(GPIO.BCM) 
GPIO.setwarnings(False)

count_work=0
count_dont=0
temp_Soll=2


#print(count_work)
def get_temp():
    global count_dont
    global count_work
    
    temp_Dach=0
    temp_Luft=0
    temp_Nachlauf=0
    temp_Vorlauf=0

    for t in range(1):
        tempfile_Vorlauf = open(Vorlauf)
        tempfile_Nachlauf = open(Nachlauf)
        tempfile_Dach = open(Dach)
        tempfile_Luft = open(Luft)
        text_Vorlauf = tempfile_Vorlauf.read() 
        text_Nachlauf = tempfile_Nachlauf.read() 
        text_Dach = tempfile_Dach.read() 
        text_Luft = tempfile_Luft.read() 
        tempfile_Luft.close() 
        tempfile_Vorlauf.close() 
        tempfile_Nachlauf.close() 
        tempfile_Dach.close() 
        tline_Luft = text_Luft.split("\n")[1] # the second line contains temperature
        tline_Vorlauf = text_Vorlauf.split("\n")[1] # the second line contains temperature
        tline_Nachlauf = text_Nachlauf.split("\n")[1] # the second line contains temperature
        tline_Dach = text_Dach.split("\n")[1] # the second line contains temperature
        tdata_Luft = tline_Luft.split(" ")[9] # position 9 contains temparature value
        tdata_Vorlauf = tline_Vorlauf.split(" ")[9] # position 9 contains temparature value
        tdata_Nachlauf = tline_Nachlauf.split(" ")[9] # position 9 contains temparature value
        tdata_Dach = tline_Dach.split(" ")[9] # position 9 contains temparature value
        temp_Dach  += float(tdata_Dach[2:])/1000
        temp_Vorlauf  += float(tdata_Vorlauf[2:])/1000
        temp_Nachlauf  += float(tdata_Nachlauf[2:])/1000
        temp_Luft  += float(tdata_Luft[2:])/1000
        temp_Delta=temp_Dach-temp_Vorlauf
   

        if (temp_Dach-temp_Vorlauf > temp_Soll):
            GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
            GPIO.setwarnings(False)
            RELAIS_1_GPIO = 21
            GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Assign mode
            GPIO.output(RELAIS_1_GPIO, GPIO.LOW) # out
            time.sleep(60)
            count_work +=1

    
        if (temp_Dach-temp_Vorlauf < temp_Soll):
            GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
            GPIO.setwarnings(False)
            RELAIS_1_GPIO = 21
            GPIO.setup(RELAIS_1_GPIO, GPIO.OUT) # GPIO Assign mode
            GPIO.output(RELAIS_1_GPIO, GPIO.LOW) # out
            time.sleep(60)
            count_dont +=1
    


        else:
            time.sleep(5)

        timestamp=datetime.datetime.utcnow().isoformat()
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
#        print(now)



while True:
    datapoints=get_temp()
    bResult=client.write_points(datapoints)
    try:
        client.write_points(datapoints)
    except Exception as exc:
        print(exc)
    #time.sleep(10)
#    clear_counter()
    # Create Influxdb datapoints (using lineprotocol as of Influxdb >1.1)
#    print("Write points {0} bResult:{0}".format(datapoints,bResult))
# Initialize the Influxdb client

#        # Write datapoints to InfluxDB
#print(count_work)
#print(count_dont)
#time.sleep(2) 
