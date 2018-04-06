#!/usr/bin/env python
 
import paho.mqtt.client as mqtt
from mqtt_settings import config
import time
import json
from sense_hat import SenseHat
from collections import OrderedDict

import datetime
import pytz

UNIX_EPOCH = datetime.datetime(1970, 1, 1, 0, 0) #offset-naive datetime
TS_MULT_us = 1e6

def now_timestamp(ts_mult=TS_MULT_us, epoch=UNIX_EPOCH):
    return(int((datetime.datetime.utcnow() - epoch).total_seconds()*ts_mult))

def all_sensors(sense):
    d_sensors = OrderedDict([
        ('pixels', sense.get_pixels),
        ('humidity', sense.get_humidity),
        ('temperature', sense.get_temperature_from_humidity),
        ('temperature_from_pressure', sense.get_temperature_from_pressure),
        ('pressure', sense.get_pressure),
        ('orientation', sense.get_orientation),
        ('compass', sense.get_compass),
        ('gyroscope', sense.get_gyroscope),
        ('accelerometer', sense.get_accelerometer),
    ])
    return d_sensors

def on_message(mosq, obj, msg):
    print("%-20s %d %s" % (msg.topic, msg.qos, msg.payload))
    mosq.publish('pong', "Thanks", 0)
 
def on_publish(mosq, obj, mid):
    print("publish %s %s %s" % (mosq, obj, mid))

def main():
    cli = mqtt.Client()
    cli.on_message = on_message
    cli.on_publish = on_publish

    #cli.tls_set('root.ca',
    #certfile='c1.crt',
    #keyfile='c1.key')

    #cli.username_pw_set("guigui", password="abloc")

    cli.connect(config['host'], config['port'], config['keepalive'])
    sense = SenseHat()
    sense.set_imu_config(True, True, True)
    d_sensors = all_sensors(sense)

    while cli.loop() == 0:
        now = datetime.datetime.now(pytz.utc)
        
        sensors = d_sensors.keys() # all sensors
        #print(sensors)

        for sensor in sensors:
            get_value = d_sensors[sensor] # get a "callable"
            #print(sensor, get_value)

            data = {
                'ts': now.isoformat(),
                'd': {
                    sensor: get_value()
                }
            }
            #print(data)
            
            payload = json.dumps(data) # serialization
            cli.publish(topic='/sensors/SenseHat01/%s' % sensor, payload=payload, qos=0, retain=False)
        
        #cli.publish(topic='/sensors/sensor01', payload=payload, qos=0, retain=False)
        #payload = json.dumps(hum) # serialization
        #cli.publish(topic='/sensors/sensor02', payload=payload, qos=0, retain=False)
        #time.sleep(1)
        #print("wait")

if __name__ == '__main__':
    main()
