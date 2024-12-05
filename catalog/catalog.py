import cherrypy
import datetime
import time
import json
import uuid

class CatalogService:

    exposed = True

    def __init__(self):
        self.broker = self.load_json("broker.json")
        self.devices = self.load_json("devices.json")

    @staticmethod
    def validateFields(required_fields, data):
        for field in required_fields:
            if field not in data:
                raise cherrypy.HTTPError(400, f"Invalid request: '{field}' is required")

    @staticmethod
    def load_json(file_name):

        try:
            with open(file_name, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    @staticmethod
    def save_json(file_name, data):
        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)

    # Periodic cleanup thread
    @staticmethod
    def periodic_cleanup():
        while True:
            devices = CatalogService.load_json("devices.json")
            current_time = datetime.utcnow()
            updated_devices = [
                device for device in devices
                if datetime.fromisoformat(device["insert-timestamp"]) > current_time - datetime.timedelta(minutes=2)
            ]
            CatalogService.save_json("devices.json", updated_devices)
            time.sleep(60)

    def GET(self, *uri, **params):
        if(uri[0] == "broker"):
            return json.dumps(self.broker).encode('utf-8')
        if(uri[0] == "devices"):
            if(len(uri) == 2):
                for device in self.devices:
                    if(device["deviceID"] == uri[1]):
                        return json.dumps(device).encode('utf-8')
                raise cherrypy.HTTPError(404, "Device not found")
            return json.dumps(self.devices).encode('utf-8')

    def POST(self, *uri, **params):
        if(uri[0] == "devices"):
            device = json.loads(cherrypy.request.body.read())
            self.validateFields(["endpoints", "availableResources"], device)
            device["deviceID"] = str(uuid.uuid4())
            device["insert-timestamp"] = datetime.datetime.now(datetime.UTC).isoformat()
            self.devices.append(device)
            self.save_json("devices.json", self.devices)
            return json.dumps(device).encode('utf-8')

    def PUT(self, *uri, **params):
        if(len(uri) == 2 and uri[0] == "devices"):
            device = json.loads(cherrypy.request.body.read())
            device["deviceID"] = uri[1]
            device["insert-timestamp"] = datetime.datetime.now(datetime.UTC).isoformat()
            self.validateFields(["endpoints", "availableResources"], device)
            for i, d in enumerate(self.devices):
                if(d["deviceID"] == uri[1]):
                    self.devices[i] = device
                    self.save_json("devices.json", self.devices)
                    return json.dumps(device).encode('utf-8')
            raise cherrypy.HTTPError(404, "Device not found")
        raise cherrypy.HTTPError(400, "Invalid request")


if __name__ == '__main__':
    conf={
        '/':{
            'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on':True
        }
    }
    cherrypy.tree.mount(CatalogService(),'/',conf)
    cherrypy.config.update({
        'server.socket_port':8080,
        "tools.response_headers.on": True,
        "tools.response_headers.headers": [("Content-Type", "application/json")]
    })
    cherrypy.engine.start()
    cherrypy.engine.block()
