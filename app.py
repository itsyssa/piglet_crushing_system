from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import RPi.GPIO as GPIO
import atexit
import time
import threading
import subprocess

app = Flask(__name__)

# =========================
# GPIO SETUP (ACTIVE LOW)
# =========================
ALARM_PIN = 17
gpio_lock = threading.Lock()

def init_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ALARM_PIN, GPIO.OUT)
    GPIO.output(ALARM_PIN, GPIO.HIGH)  # OFF state

init_gpio()

def cleanup_gpio():
    print("CLEANUP GPIO", flush=True)
    GPIO.output(ALARM_PIN, GPIO.HIGH)
    GPIO.cleanup()

atexit.register(cleanup_gpio)

# =========================
# SIREN PROCESS CONTROL
# =========================
siren_process = None

# =========================
# DATABASE SETUP
# =========================
DB_PATH = "piglet_crushing.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crushing_id TEXT,
            date TEXT,
            event_timestamp TEXT,
            crushing_duration TEXT,
            alarm TEXT,
            alarm_timestamp TEXT,
            image_path TEXT,
            video_path TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# =========================
# QUERY EVENTS
# =========================
def query_events(filters=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = "SELECT * FROM events WHERE 1=1"
    params = []

    if filters:
        if filters.get('start_date'):
            query += " AND date >= ?"
            params.append(filters['start_date'])
        if filters.get('end_date'):
            query += " AND date <= ?"
            params.append(filters['end_date'])

    c.execute(query, params)
    results = [dict(row) for row in c.fetchall()]
    conn.close()
    return results

# =========================
# ROUTES
# =========================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events')
def api_events():
    filters = {
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date')
    }
    filters = {k: v for k, v in filters.items() if v}
    return jsonify({"events": query_events(filters)})

# =========================
# AI DETECTION → START SIREN
# =========================
@app.route('/detect', methods=['POST'])
def detect():
    global siren_process

    data = request.get_json()

    if data.get("crushing", False):
        if siren_process is None:
            print("CRUSHING DETECTED → STARTING try.py LOOP")

            siren_process = subprocess.Popen(
                ["python", "try.py"]
            )

    return jsonify({"status": "received"})

# =========================
# STOP BUTTON (CTRL+C EQUIVALENT)
# =========================
@app.route('/alarm/off')
def alarm_off():
    global siren_process

    print("STOP BUTTON PRESSED → TERMINATING PROCESS")

    if siren_process:
        siren_process.terminate()  # <-- THIS IS YOUR CTRL+C EQUIVALENT
        siren_process = None

    with gpio_lock:
        GPIO.output(ALARM_PIN, GPIO.HIGH)

    return jsonify({"status": "STOPPED"})

# =========================
# TEST ROUTE
# =========================
@app.route('/test')
def test():
    with gpio_lock:
        GPIO.output(ALARM_PIN, GPIO.LOW)
        time.sleep(1)
        GPIO.output(ALARM_PIN, GPIO.HIGH)
    return "TEST DONE"

# =========================
# RUN SERVER
# =========================
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True,
        use_reloader=False
    )
