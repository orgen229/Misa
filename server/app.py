from flask import Flask, request, jsonify, render_template, send_file
from datetime import datetime
import sqlite3
import csv
import os

app = Flask(__name__)

DATABASE = "measurements.db"
CSV_FILE = "measurements.csv"

system_state = {
    "system_open": False,
    "monitoring_active": False,
    "fan_on_threshold": 33.0,
    "fan_off_threshold": 32.0,
    "measurement_interval": 5000
}


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

    # Migration for older database versions
    cursor.execute("PRAGMA table_info(measurements)")
    columns = [row[1] for row in cursor.fetchall()]

    if "fan_state" not in columns:
        cursor.execute("ALTER TABLE measurements ADD COLUMN fan_state TEXT NOT NULL DEFAULT 'OFF'")

    if "fan_on_threshold" not in columns:
        cursor.execute("ALTER TABLE measurements ADD COLUMN fan_on_threshold REAL NOT NULL DEFAULT 33.0")

    if "fan_off_threshold" not in columns:
        cursor.execute("ALTER TABLE measurements ADD COLUMN fan_off_threshold REAL NOT NULL DEFAULT 32.0")

    conn.commit()
    conn.close()

    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "timestamp",
                "temperature",
                "humidity",
                "sensor",
                "unit_temperature",
                "unit_humidity",
                "fan_state",
                "fan_on_threshold",
                "fan_off_threshold"
            ])


def insert_measurement(temperature, humidity, sensor, unit_temperature,
                       unit_humidity, fan_state, fan_on_threshold,
                       fan_off_threshold, timestamp):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO measurements
        (temperature, humidity, sensor, unit_temperature, unit_humidity,
         fan_state, fan_on_threshold, fan_off_threshold, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        temperature,
        humidity,
        sensor,
        unit_temperature,
        unit_humidity,
        fan_state,
        fan_on_threshold,
        fan_off_threshold,
        timestamp
    ))

    conn.commit()
    conn.close()


def write_measurement_to_csv(temperature, humidity, sensor, unit_temperature,
                             unit_humidity, fan_state, fan_on_threshold,
                             fan_off_threshold, timestamp):
    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "temperature",
                "humidity",
                "sensor",
                "unit_temperature",
                "unit_humidity",
                "fan_state",
                "fan_on_threshold",
                "fan_off_threshold"
            ])

        writer.writerow([
            timestamp,
            temperature,
            humidity,
            sensor,
            unit_temperature,
            unit_humidity,
            fan_state,
            fan_on_threshold,
            fan_off_threshold
        ])


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/open", methods=["POST"])
def open_system():
    system_state["system_open"] = True
    system_state["monitoring_active"] = False

    return jsonify({
        "status": "ok",
        "message": "System initialized",
        "state": system_state
    })


@app.route("/api/start", methods=["POST"])
def start_monitoring():
    if not system_state["system_open"]:
        return jsonify({
            "status": "error",
            "message": "System must be opened first"
        }), 400

    system_state["monitoring_active"] = True

    return jsonify({
        "status": "ok",
        "message": "Monitoring started",
        "state": system_state
    })


@app.route("/api/stop", methods=["POST"])
def stop_monitoring():
    system_state["monitoring_active"] = False

    return jsonify({
        "status": "ok",
        "message": "Monitoring stopped",
        "state": system_state
    })


@app.route("/api/close", methods=["POST"])
def close_system():
    system_state["monitoring_active"] = False
    system_state["system_open"] = False

    return jsonify({
        "status": "ok",
        "message": "System closed",
        "state": system_state
    })


@app.route("/api/config", methods=["GET", "POST"])
def config():
    if request.method == "POST":
        data = request.get_json()

        if data is None:
            return jsonify({
                "status": "error",
                "message": "No JSON received"
            }), 400

        fan_on = data.get("fan_on_threshold")
        fan_off = data.get("fan_off_threshold")
        interval = data.get("measurement_interval")

        if fan_on is not None:
            system_state["fan_on_threshold"] = float(fan_on)

        if fan_off is not None:
            system_state["fan_off_threshold"] = float(fan_off)

        if interval is not None:
            system_state["measurement_interval"] = int(interval)

        if system_state["fan_off_threshold"] >= system_state["fan_on_threshold"]:
            return jsonify({
                "status": "error",
                "message": "Fan OFF threshold must be lower than Fan ON threshold"
            }), 400

        return jsonify({
            "status": "ok",
            "message": "Configuration updated",
            "state": system_state
        })

    return jsonify(system_state)


@app.route("/api/state", methods=["GET"])
def get_state():
    return jsonify(system_state)


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
    fan_state = data.get("fan_state", "OFF")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if temperature is None or humidity is None:
        return jsonify({
            "status": "error",
            "message": "Missing temperature or humidity"
        }), 400

    # Data are accepted by the server, but stored only when the web application is opened and started.
    if not system_state["system_open"] or not system_state["monitoring_active"]:
        return jsonify({
            "status": "ignored",
            "message": "System is not open or monitoring is stopped",
            "state": system_state
        }), 200

    fan_on_threshold = system_state["fan_on_threshold"]
    fan_off_threshold = system_state["fan_off_threshold"]

    insert_measurement(
        temperature,
        humidity,
        sensor,
        unit_temperature,
        unit_humidity,
        fan_state,
        fan_on_threshold,
        fan_off_threshold,
        timestamp
    )

    write_measurement_to_csv(
        temperature,
        humidity,
        sensor,
        unit_temperature,
        unit_humidity,
        fan_state,
        fan_on_threshold,
        fan_off_threshold,
        timestamp
    )

    print("----- NEW DATA SAVED -----")
    print("Time:", timestamp)
    print("Sensor:", sensor)
    print("Temperature:", temperature)
    print("Humidity:", humidity)
    print("Fan state:", fan_state)

    return jsonify({
        "status": "ok",
        "message": "Data received and saved",
        "time": timestamp,
        "temperature": temperature,
        "humidity": humidity,
        "fan_state": fan_state,
        "state": system_state
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
            "message": "No data available",
            "state": system_state
        }), 404

    return jsonify({
        "id": row["id"],
        "temperature": row["temperature"],
        "humidity": row["humidity"],
        "sensor": row["sensor"],
        "unit_temperature": row["unit_temperature"],
        "unit_humidity": row["unit_humidity"],
        "fan_state": row["fan_state"],
        "fan_on_threshold": row["fan_on_threshold"],
        "fan_off_threshold": row["fan_off_threshold"],
        "timestamp": row["timestamp"],
        "state": system_state
    })


@app.route("/api/history", methods=["GET"])
def history_data():
    mode = request.args.get("mode", default="last20", type=str)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if mode == "24h":
        cursor.execute("""
            SELECT * FROM measurements
            WHERE datetime(timestamp) >= datetime('now', '-24 hours')
            ORDER BY id ASC
        """)
    else:
        cursor.execute("""
            SELECT * FROM measurements
            ORDER BY id DESC
            LIMIT 20
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
            "fan_state": row["fan_state"],
            "fan_on_threshold": row["fan_on_threshold"],
            "fan_off_threshold": row["fan_off_threshold"],
            "timestamp": row["timestamp"]
        })

    if mode == "last20":
        history.reverse()

    return jsonify(history)


@app.route("/api/file-history", methods=["GET"])
def file_history():
    limit = request.args.get("limit", default=20, type=int)

    if not os.path.exists(CSV_FILE):
        return jsonify([])

    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = list(csv.DictReader(file))

    rows = reader[-limit:]

    return jsonify(rows)


@app.route("/api/download-csv", methods=["GET"])
def download_csv():
    if not os.path.exists(CSV_FILE):
        return jsonify({
            "status": "error",
            "message": "CSV file does not exist"
        }), 404

    return send_file(CSV_FILE, as_attachment=True)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
