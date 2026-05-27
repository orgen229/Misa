from flask import Flask, request, jsonify, render_template
from datetime import datetime
import sqlite3

app = Flask(__name__)

DATABASE = "measurements.db"


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            sensor TEXT NOT NULL,
            unit_temperature TEXT NOT NULL,
            unit_humidity TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def insert_measurement(temperature, humidity, sensor, unit_temperature, unit_humidity, timestamp):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO measurements
        (temperature, humidity, sensor, unit_temperature, unit_humidity, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (temperature, humidity, sensor, unit_temperature, unit_humidity, timestamp))

    conn.commit()
    conn.close()


@app.route("/")
def dashboard():
    return render_template("index.html")


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
    unit_temperature = data.get("unit_temperature", "C")
    unit_humidity = data.get("unit_humidity", "%")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if temperature is None or humidity is None:
        return jsonify({
            "status": "error",
            "message": "Missing temperature or humidity"
        }), 400

    insert_measurement(
        temperature,
        humidity,
        sensor,
        unit_temperature,
        unit_humidity,
        timestamp
    )

    print("----- NEW DATA SAVED -----")
    print("Time:", timestamp)
    print("Sensor:", sensor)
    print("Temperature:", temperature)
    print("Humidity:", humidity)

    return jsonify({
        "status": "ok",
        "message": "Data received and saved",
        "time": timestamp,
        "temperature": temperature,
        "humidity": humidity
    }), 200


@app.route("/api/latest", methods=["GET"])
def latest_data():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM measurements
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({
            "status": "error",
            "message": "No data available"
        }), 404

    return jsonify({
        "id": row["id"],
        "temperature": row["temperature"],
        "humidity": row["humidity"],
        "sensor": row["sensor"],
        "unit_temperature": row["unit_temperature"],
        "unit_humidity": row["unit_humidity"],
        "timestamp": row["timestamp"]
    })


@app.route("/api/history", methods=["GET"])
def history_data():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM measurements
        ORDER BY id DESC
        LIMIT 100
    """)

    rows = cursor.fetchall()
    conn.close()

    history = []

    for row in rows:
        history.append({
            "id": row["id"],
            "temperature": row["temperature"],
            "humidity": row["humidity"],
            "sensor": row["sensor"],
            "unit_temperature": row["unit_temperature"],
            "unit_humidity": row["unit_humidity"],
            "timestamp": row["timestamp"]
        })

    history.reverse()

    return jsonify(history)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
