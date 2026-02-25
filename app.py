from flask import Flask, render_template, request, send_file, jsonify
import sqlite3
import os
from datetime import datetime
import csv

app = Flask(__name__)

# --- DATABASE SETUP ---
DB_PATH = "piglet_crushing.db"

def init_db():
    """Initialize the SQLite database and table if not exists"""
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
            image_path TEXT
        )
    """)
    conn.commit()
    conn.close()

# Call once at startup
init_db()

# --- HELPER FUNCTIONS ---
def save_event(event):
    """Save an event dict to the database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO events (crushing_id, date, event_timestamp, crushing_duration, alarm, alarm_timestamp, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        event['Crushing ID'],
        event['Date'],
        event['Event Timestamp'],
        event['Crushing Duration'],
        event['Alarm'],
        event['Alarm Timestamp'],
        event['Image Path']
    ))
    conn.commit()
    conn.close()

def query_events(filters=None):
    """Query events from the database with optional filters"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    query = "SELECT * FROM events WHERE 1=1"
    params = []

    if filters:
        if 'start_date' in filters:
            query += " AND date >= ?"
            params.append(filters['start_date'])
        if 'end_date' in filters:
            query += " AND date <= ?"
            params.append(filters['end_date'])
        if 'min_duration' in filters:
            query += " AND (cast(strftime('%s', crushing_duration) as integer) >= ?)"
            params.append(filters['min_duration'])
        if 'max_duration' in filters:
            query += " AND (cast(strftime('%s', crushing_duration) as integer) <= ?)"
            params.append(filters['max_duration'])
        if 'min_id' in filters:
            query += " AND id >= ?"
            params.append(filters['min_id'])
        if 'max_id' in filters:
            query += " AND id <= ?"
            params.append(filters['max_id'])

    c.execute(query, params)
    results = [dict(row) for row in c.fetchall()]
    conn.close()
    return results

# --- ROUTES ---
@app.route('/')
def index():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template('index.html', current_time=current_time)

@app.route('/api/events')
def api_events():
    filters = {
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'min_duration': request.args.get('min_duration'),
        'max_duration': request.args.get('max_duration'),
        'min_id': request.args.get('min_id'),
        'max_id': request.args.get('max_id'),
    }
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    events = query_events(filters)
    return jsonify({"events": events})

@app.route('/api/export-csv')
def export_csv():
    events = query_events()
    csv_path = "exports/events_export.csv"
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Crushing ID','Date','Event Timestamp','Crushing Duration','Alarm','Alarm Timestamp','Image Path'])
        writer.writeheader()
        for e in events:
            writer.writerow(e)

    return send_file(csv_path, as_attachment=True)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(f'images/event_images/{filename}', as_attachment=True)

@app.route('/alarm/off')
def alarm_off():
    # GPIO code to turn siren OFF goes here
    print("Alarm OFF triggered")
    return "OK"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)