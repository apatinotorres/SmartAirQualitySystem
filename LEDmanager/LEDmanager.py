from MyMQTT import MyMQTT
import json
import cherrypy
import time
class LightManager: 
    def __init__(self, clientID, broker, port):
        self.broker = broker
        self.port = port
        self.rooms = {}  # Store room configurations internally
        self.clientID = clientID
        self.client = MyMQTT(clientID, broker, port, self)
        self.colors = ["green", "yellow", "orange", "red", "dark purple"]
        self.eaqi_thresholds = {
            "PM2.5": [10, 20, 25, 50],
            "PM10": [20, 40, 50, 100],
            "O3": [60, 120, 180, 240],
            "NO2": [40, 90, 120, 230],
            "SO2": [100, 200, 350, 500]
        }

    def add_room(self, room_id):
        """Add a new room and initialize its configurations."""
        topics_subscribe = [f"{room_id}/{pollutant}" for pollutant in ["PM2.5", "PM10", "O3", "NO2", "SO2"]]
        topic_publish = f"{room_id}/LED"
        self.rooms[room_id] = {
            "topics_subscribe": topics_subscribe,
            "topic_publish": topic_publish,
            "latest_values": {pollutant: 0 for pollutant in ["PM2.5", "PM10", "O3", "NO2", "SO2"]},
            "current_color": "green"
        }
        print(f"Added room {room_id} with topics: {topics_subscribe} and LED topic: {topic_publish}")

    def startSim(self):
        """Start MQTT client and subscribe to all room topics."""
        self.client.start()
        for room_id, room_details in self.rooms.items():
            for topic in room_details["topics_subscribe"]:
                self.client.mySubscribe(topic)

    def stopSim(self):
        """Stop MQTT client."""
        self.client.unsubscribe()
        self.client.stop()

    def notify(self, topic, msg):
        print(f"Message received on topic {topic}: {msg}")
        try:
            data = json.loads(msg)
            room_id, pollutant = topic.split("/")[:2]
            if room_id in self.rooms:
                room = self.rooms[room_id]
                room["latest_values"][pollutant] = data["value"]
                room["current_color"] = self.determine_led_color(room["latest_values"])
                self.publish(room_id, room["current_color"])
        except Exception as e:
            print(f"Error processing message: {e}")

    def determine_led_color(self, latest_values):
        # Determine the worst score across pollutants
        worst_score = 0
        for pollutant, thresholds in self.eaqi_thresholds.items():
            value = latest_values.get(pollutant, 0)
            for index, threshold in enumerate(thresholds):
                if value > threshold:
                    worst_score = max(worst_score, index + 1)
        return self.colors[worst_score]

    def publish(self, room_id, color):
        message = {
            'client': self.clientID,
            'room_id': room_id,
            'n': 'switch',
            'status': color,
            'timestamp': time.time(),
            'unit': "color"
        }
        topic_publish = self.rooms[room_id]["topic_publish"]
        self.client.myPublish(topic_publish, message)
        print(f"LED color set to {color} for room {room_id}")

if __name__ == "__main__":
    broker = "YOU NEED TO FILL IN THE BROKER ADDRESS HERE"
    port = "YOU NEED TO FILL IN THE PORT HERE"
    
    light_manager = LightManager("light_manager", broker, port)
    
    # Dynamically add rooms
    light_manager.add_room("room1")
    light_manager.add_room("room2")
    
    cherrypy.engine.subscribe('start', light_manager.startSim)
    cherrypy.engine.subscribe('stop', light_manager.stopSim)
    
    cherrypy.quickstart(light_manager, "/", {"global": {"server.socket_host": "0.0.0.0", "server.socket_port": 8080}})
