from flask import Flask, jsonify, request

app = Flask(__name__)

received_data = None

# TARGET_SYSTEM_URL = "http://<target-microservice>:<port>/endpoint"

@app.route('/', methods=['GET'])
def home():
    """
    Endpoint pour vérifier que l'API fonctionne.
    """
    return jsonify({"status": "success", "message": "Weather Adaptor API is running"}), 200


@app.route('/receive-json', methods=['POST'])
def receive_json():
    """
    Endpoint pour recevoir des données JSON envoyées par weather.py.
    """
    global received_data
    try:
        # Get entering JSON data
        received_data = request.get_json()
        if not received_data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        # Sanity check
        print("Received JSON data (first line):", received_data[0])

        # Uncomment after to the target microservice:
        # send_to_target_system(received_data)

        return jsonify({"status": "success", "message": "Data received successfully"}), 200
    except Exception as e:
        print(f"Error receiving data: {e}")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500


@app.route('/data', methods=['GET'])
def get_data():
    """
    Endpoint pour afficher la première ligne des données JSON reçues.
    """
    if received_data is None:
        return jsonify({"status": "error", "message": "No data received yet"}), 404

    # Show the first line for sanity check
    return jsonify({"first_line": received_data[0]}), 200


def send_to_target_system(data):
    """
    Fonction pour envoyer les données JSON au microservice cible.
    """
    try:
        # prepare to send JSONs
        headers = {"Content-Type": "application/json"}
        # Change  <TARGET_SYSTEM_URL> when we will have it
        response = requests.post(TARGET_SYSTEM_URL, json=data, headers=headers)

        if response.status_code == 200:
            print("Data successfully sent to target system.")
        else:
            print(f"Failed to send data to target system. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error sending data to target system: {e}")


if __name__ == "__main__":
    print("Starting Weather Adaptor API on port 5000...")
    app.run(host="0.0.0.0", port=5000)
