import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import cv2
from datetime import datetime
import json
from pathlib import Path

from ultralytics import YOLO
import joblib
import numpy as np

from .camera_streams import get_video_captures
from .ai_agent import choose_road_to_open
from .logger import log_traffic_data
from yolov8_model.traffic_detector import process_frame
from ReinforcementLearning.predict import predict_duration

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

# Load models
yolo_model = YOLO("./yolov8_model/yolov8n.pt")
rl_model = joblib.load("backend/ml_model/model.pkl")

# Initialize video streams
caps = get_video_captures()

# Logs file
LOG_FILE = Path("backend/traffic_logs.json")
if not LOG_FILE.exists():
    LOG_FILE.write_text(json.dumps([]))

# --- 1. Video stream endpoint ---
VIDEO_PATHS = {
    "north": os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/north.mp4')),
    "south": os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/south.mp4')),
    "east": os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/east.mp4')),
    "west": os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/west.mp4')),
}

def gen_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    cap.release()

@app.get("/api/video/{direction}")
def video_feed(direction: str):
    video_path = VIDEO_PATHS.get(direction)
    if not video_path or not os.path.exists(video_path):
        return JSONResponse({"error": "Video not found"}, status_code=404)
    return StreamingResponse(gen_frames(video_path), media_type="multipart/x-mixed-replace; boundary=frame")

# --- 2. Real-time vehicle detections ---
@app.get("/api/detections")
def get_detections():
    vehicle_counts = {}
    for road, cap in caps.items():
        ret, frame = cap.read()
        if not ret:
            vehicle_counts[road] = {"vehicles": 0}
            continue
        frame = cv2.resize(frame, (640, 480))
        _, count = process_frame(frame, yolo_model, road)
        vehicle_counts[road] = {"vehicles": count}
    return vehicle_counts

# --- 3. Traffic light AI decision ---
@app.get("/api/traffic-light")
def get_traffic_light():
    road_counts = {}
    for road, cap in caps.items():
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.resize(frame, (640, 480))
        _, count = process_frame(frame, yolo_model, road)
        road_counts[road] = count

    green_road = choose_road_to_open(road_counts)
    duration = predict_duration(road_counts, green_road)
    log_traffic_data(road_counts, green_road, duration)

    state = {dir: "red" for dir in road_counts}
    state[green_road] = "green"

    log_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": f"Green to {green_road} for {duration}s"
    }

    logs = json.loads(LOG_FILE.read_text())
    logs.insert(0, log_entry)
    LOG_FILE.write_text(json.dumps(logs[:50]))  # Keep last 50 logs

    return {
        "green": green_road,
        "duration": duration,
        "states": state
    }

# --- 4. View logs ---
@app.get("/api/logs")
def get_logs():
    logs = json.loads(LOG_FILE.read_text())
    return {"logs": logs}

# --- 5. Summary stats ---
@app.get("/api/stats")
def get_stats():
    road_counts = {}
    total = 0
    for road, cap in caps.items():
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.resize(frame, (640, 480))
        _, count = process_frame(frame, yolo_model, road)
        road_counts[road] = count
        total += count

    # Simplified wait time estimate
    average_wait = np.mean(list(road_counts.values())) * 2  # seconds per car, adjust as needed

    return {
        "total_vehicles": total,
        "average_wait_time": round(average_wait, 2)
    }