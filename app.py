from flask import Flask, render_template, request, send_file, jsonify
import csv
from datetime import datetime

app = Flask(__name__)

# Load events from CSV
def load_events():
    events = []
    with open('logs/events.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            events.append(row)
    return events

# Convert duration string "HH:MM:SS" to seconds
def duration_to_seconds(duration):
    h, m, s = [int(x) for x in duration.split(":")]
    return h*3600 + m*60 + s

# Main page
@app.route('/')
def index():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template('index.html', current_time=current_time)

# API to fetch events with filters
@app.route('/api/events')
def api_events():
    events = load_events()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    min_duration = request.args.get('min_duration')
    max_duration = request.args.get('max_duration')
    min_id = request.args.get('min_id')
    max_id = request.args.get('max_id')

    filtered = []
    for e in events:
        add = True
        # Filter by date
        if start_date:
            add &= e['Date'] >= start_date
        if end_date:
            add &= e['Date'] <= end_date
        # Filter by duration
        dur = duration_to_seconds(e['Crushing Duration'])
        if min_duration:
            add &= dur >= int(min_duration)
        if max_duration:
            add &= dur <= int(max_duration)
        # Filter by Crushing ID
        if min_id:
            add &= int(e['Crushing ID'].split()[-1]) >= int(min_id)
        if max_id:
            add &= int(e['Crushing ID'].split()[-1]) <= int(max_id)
        if add:
            filtered.append(e)

    return jsonify({"events": filtered})

# Export CSV with filters
@app.route('/api/export-csv')
def export_csv():
    return send_file('logs/events.csv', as_attachment=True)

# Download image
@app.route('/download/<filename>')
def download_file(filename):
    return send_file(f'images/event_images/{filename}', as_attachment=True)

# Alarm OFF endpoint
@app.route('/alarm/off')
def alarm_off():
    # GPIO code to turn siren OFF here
    print("Alarm OFF triggered")
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
