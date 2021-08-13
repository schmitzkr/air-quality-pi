#!/usr/bin/env python3
import time
from datetime import datetime
from sds011 import *
import aqi
import psutil
import paho.mqtt.publish as publish
import urllib, urllib3
import os
import tweepy
import json
import config

sensor = SDS011("/dev/ttyUSB0")

def get_data(n=3):
        sensor.sleep(sleep=False)
        pmt_2_5 = 0
        pmt_10 = 0
        time.sleep(10)
        for i in range (n):
            x = sensor.query()
            pmt_2_5 = pmt_2_5 + x[0]
            pmt_10 = pmt_10 + x[1]
            time.sleep(2)
        pmt_2_5 = round(pmt_2_5/n, 1)
        pmt_10 = round(pmt_10/n, 1)
        sensor.sleep(sleep=True)
        time.sleep(2)
        return pmt_2_5, pmt_10

def conv_aqi(pmt_2_5, pmt_10):
    aqi_2_5 = aqi.to_iaqi(aqi.POLLUTANT_PM25, str(pmt_2_5))
    aqi_10 = aqi.to_iaqi(aqi.POLLUTANT_PM10, str(pmt_10))
    return aqi_2_5, aqi_10

#twitter stuff
with open('twitterauth.json') as file:
    secrets = json.load(file)
    auth = tweepy.OAuthHandler(secrets['consumerKey'], secrets['consumerSecret'])
    auth.set_access_token(secrets['token'], secrets['tokenSecret'])
    twitter = tweepy.API(auth)

#thingspeak stuff
topic = "channels/" + config.channelID + "/publish/" + config.apiKey
mqttHost = "mqtt.thingspeak.com"

tTransport = "tcp"
tPort = 1883
tTLS = None

while True:        
    pmt_2_5, pmt_10 = get_data()
    aqi_2_5, aqi_10 = conv_aqi(pmt_2_5, pmt_10)
    tPayload = "field1=" + str(pmt_2_5)+ "&field2=" + str(aqi_2_5)+ "&field3=" + str(pmt_10)+ "&field4=" + str(aqi_10)
    try:
        
        publish.single(topic, payload=tPayload, hostname=config.mqttHost, port=tPort, tls=tTLS, transport=tTransport)
        if aqi_10 > 40:
            twitter.update_status('Tweet the AQI if it is over 10, AQI: '+str(aqi_10)+' PMT2.5: '+str(pmt_2_5))
        time.sleep(60)
    except Exception as e: print(e)
        #print ("[INFO] Failure in sending data")
    time.sleep(12)