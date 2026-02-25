import cv2
import os
from datetime import datetime
import sqlite3

# --- CONFIG ---
DB_PATH = "piglet_crushing.db"
IMAGE_DIR = "static/images/event_images"
VIDEO_DIR = "static/videos"
VIDEO_FPS = 20
VIDEO_DURATION_SEC = 5  # record 5 seconds for each event
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

# --- SAVE TO DATABASE ---
def save_event_to_db(crushing_id, duration, alarm, image_path, video_path):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO events 
        (crushing_id, date, event_timestamp, crushing_duration, alarm, alarm_timestamp, image_path, video_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        crushing_id,
        timestamp.split()[0],
        timestamp,
        duration,
        alarm,
        timestamp,
        image_path,
        video_path
    ))
    conn.commit()
    conn.close()
    print(f"[DB] Saved event {crushing_id}")

# --- CAPTURE IMAGE & VIDEO ---
def capture_event(crushing_id="Crushing 1", duration="00:00:05", alarm="Activated"):
    cap = cv2.VideoCapture(0)  # Pi camera
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # --- IMAGE ---
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        cap.release()
        return
    image_filename = f"{crushing_id}_{timestamp}.jpg"
    image_path = os.path.join(IMAGE_DIR, image_filename)
    cv2.imwrite(image_path, frame)
    print(f"[Camera] Saved image: {image_filename}")

    # --- VIDEO ---
    video_filename = f"{crushing_id}_{timestamp}.mp4"
    video_path = os.path.join(VIDEO_DIR, video_filename)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, VIDEO_FPS, (FRAME_WIDTH, FRAME_HEIGHT))

    frames_to_record = VIDEO_FPS * VIDEO_DURATION_SEC
    for _ in range(frames_to_record):
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    out.release()
    cap.release()
    print(f"[Camera] Saved video: {video_filename}")

    # --- SAVE TO DATABASE ---
    save_event_to_db(crushing_id, duration, alarm, image_path, video_path)