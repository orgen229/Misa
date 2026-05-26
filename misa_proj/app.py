from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return "ESP32 Flask server is running"

@app.route("/api/data", methods=["POST"])
def receive_data():
    data = request.get_json()

    if data is None:
        return jsonify({
            "status": "error",
            "message": "No JSON received"
        }), 400

    temperature = data.get("temperature")
    humidity = data.get("humidity")
    sensor = data.get("sensor", "unknown")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("----- NEW DATA -----")
    print("Time:", timestamp)
    print("Sensor:", sensor)
    print("Temperature:", temperature)
    print("Humidity:", humidity)

    return jsonify({
        "status": "ok",
        "message": "Data received",
        "time": timestamp,
        "temperature": temperature,
        "humidity": humidity
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)