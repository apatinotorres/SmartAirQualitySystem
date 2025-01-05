import paho.mqtt.client as mqtt
import cherrypy
import threading
import json
import random
import time
class RestAPI():
    def __init__(self, assigned_ip, catalog_ip):
        self.ip = assigned_ip
        self.catalog_ip = catalog_ip





class Sensors():
    def __init__(self, interval, shape, scale):
        self.PM2 = None
        self.O3 = None
        self.NO2 = None
        self.SO2 = None
        self.interval = interval
        self.shape = shape
        self.scale = scale
    def get_sensor(self, sensor_name):
        reading = random.weibullvariate(self.shape, self.scale)
        return reading

    def read_periodically(self):
        while True:
            self.PM2 = self.get_sensor('PM2')
            self.O3 = self.get_sensor('O3')
            self.NO2 = self.get_sensor('NO2')
            self.SO2 = self.get_sensor('SO2')
            print(f"PM2: {self.PM2}, O3: {self.O3}, NO2: {self.NO2}, SO2: {self.SO2}")
            time.sleep(self.interval)

    def start_reading(self):
        thread = threading.Thread(target=self.read_periodically, daemon=True)
        thread.start()


if __name__ == "__main__":
    api = RestAPI("192.168.0.1", "127.0.0.1" )
    #print(api.ip)

    sensors = Sensors(interval=1, shape=2, scale=1)
    sensors.start_reading()

    try:
        while True:
            time.sleep(1)  # Keep the main program running
    except KeyboardInterrupt:
        print("Program stopped.")
