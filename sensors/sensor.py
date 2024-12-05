import paho.mqtt.client as mqtt
import cherrypy
import threading
import json
# Function to load configuration from a JSON file
def load_config(file_name):
    try:
        with open(file_name, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: Configuration file {file_name} not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Configuration file {file_name} is not a valid JSON.")
        return {}

# Load MQTT Configuration
mqtt_config = load_config("sensor_static_MQTT_info.txt")
MQTT_BROKER = mqtt_config.get("broker", "localhost")
print(MQTT_BROKER, "++++++++++++++")
MQTT_PORT = mqtt_config.get("port", 1883)
MQTT_TOPIC = mqtt_config.get("topic", "sensor/data")

# Load REST Configuration
rest_config = load_config("sensor_static_REST_info.txt")
REST_HOST = rest_config.get("host", "0.0.0.0")
REST_PORT = rest_config.get("port", 8080)

# Global variable to store sensor data
sensor_data = {}

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global sensor_data
    print(f"Received message from {msg.topic}: {msg.payload.decode()}")
    sensor_data[msg.topic] = msg.payload.decode()

# CherryPy REST API
class SensorAPI:
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def sensor(self, **kwargs):
        """GET method to retrieve the latest sensor data."""
        return sensor_data

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def set_sensor(self, **kwargs):
        """POST method to simulate setting sensor data."""
        global sensor_data
        input_data = cherrypy.request.json
        sensor_data.update(input_data)
        return {"status": "success", "updated_data": input_data}

# MQTT Thread
def mqtt_thread():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# Main Script
if __name__ == "__main__":
    # Start MQTT thread
    mqtt_thread_instance = threading.Thread(target=mqtt_thread, daemon=True)
    mqtt_thread_instance.start()

    # Configure and start CherryPy server
    cherrypy.config.update({
        "server.socket_host": REST_HOST,
        "server.socket_port": REST_PORT,
    })
    cherrypy.quickstart(SensorAPI())
