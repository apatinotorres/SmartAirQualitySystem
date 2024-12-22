from flask import Flask, request, jsonify
import requests


# Still have to dockerize this part and work more on it

app = Flask(__name__)

# Target URL, to update when we will have more insights
TARGET_SYSTEM_URL = "http://example.com/api/data" 


@app.route('/receive-json', methods=['POST'])
def receive_json():
    """
    Endpoint to receive the JSON via REST.
    """
    try:
        # Get the JSON sent by the weather API
        incoming_data = request.get_json()
        if not incoming_data:
            return jsonify({"status": "error", "message": "No JSON received"}), 400

        print("Received JSON:", incoming_data)

        # Send the data to the system
        response_status = send_to_target_system(incoming_data)

        if response_status:
            return jsonify({"status": "success", "message": "Data forwarded to target system"}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to send data to target system"}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500


def send_to_target_system(data):
    """
    Send the JSON to the system via REST.
    """
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(TARGET_SYSTEM_URL, json=data, headers=headers)

        if response.status_code == 200:
            print("Data successfully sent to target system.")
            return True
        else:
            print(f"Failed to send data. Status code: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error sending data to target system: {e}")
        return False


if __name__ == "__main__":
    # Launch the Flask server
    app.run(host="0.0.0.0", port=5001)
