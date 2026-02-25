from flask import Flask, render_template, request, send_file, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# --- CONFIG ---
DB_PATH = "piglet_crushing.db"
IMAGE_DIR = "static/images"
VIDEO_DIR = "static/videos"

# --- DATABASE SETUP ---
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
            image_path TEXT,
            video_path TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()  # Call once at startup

# --- HELPER FUNCTIONS ---
def save_event_to_db(event):
    """Save an event dict to the database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO events 
        (crushing_id, date, event_timestamp, crushing_duration, alarm, alarm_timestamp, image_path, video_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event['crushing_id'],
        event['date'],
        event['event_timestamp'],
        event['crushing_duration'],
        event['alarm'],
        event['alarm_timestamp'],
        event['image_path'],
        event['video_path']
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
        if 'min_id' in filters:
            query += " AND id >= ?"
            params.append(filters['min_id'])
        if 'max_id' in filters:
            query += " AND id <= ?"
            params.append(filters['max_id'])
        if 'min_duration' in filters:
            query += " AND crushing_duration >= ?"
            params.append(filters['min_duration'])
        if 'max_duration' in filters:
            query += " AND crushing_duration <= ?"
            params.append(filters['max_duration'])

    c.execute(query, params)
    results = [dict(row) for row in c.fetchall()]
    conn.close()
    return results

# --- ROUTES ---
@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/events')
def api_events():
    """Return events as JSON with optional filters"""
    filters = {
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'min_id': request.args.get('min_id'),
        'max_id': request.args.get('max_id'),
        'min_duration': request.args.get('min_duration'),
        'max_duration': request.args.get('max_duration')
    }
    filters = {k: v for k, v in filters.items() if v is not None and v != ''}
    events = query_events(filters)
    return jsonify({"events": events})

@app.route('/api/export-csv')
def export_csv():
    """Export all events as CSV"""
    import csv
    events = query_events()
    csv_path = "exports/events_export.csv"
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            'crushing_id','date','event_timestamp','crushing_duration',
            'alarm','alarm_timestamp','image_path','video_path'
        ])
        writer.writeheader()
        for e in events:
            writer.writerow(e)

    return send_file(csv_path, as_attachment=True)

@app.route('/download/image/<filename>')
def download_image(filename):
    """Download an event image"""
    path = os.path.join(IMAGE_DIR, filename)
    if not os.path.exists(path):
        return "File not found", 404
    return send_file(path, as_attachment=True)

@app.route('/download/video/<filename>')
def download_video(filename):
    """Download an event video"""
    path = os.path.join(VIDEO_DIR, filename)
    if not os.path.exists(path):
        return "File not found", 404
    return send_file(path, as_attachment=True)

@app.route('/alarm/off')
def alarm_off():
    """Turn off alarm (GPIO code goes here)"""
    print("Alarm OFF triggered")
    return "OK"

# --- MAIN ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)