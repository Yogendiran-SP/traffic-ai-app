import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import cv2
from datetime import datetime
import json
from pathlib import Path
import numpy as np
import joblib
from ultralytics import YOLO

from .ai_agent import choose_road_to_open
from .logger import log_traffic_data
from .ReinforcementLearning.predict import predict_duration
from .simulator import generate_live_traffic   # NEW

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
rl_model = joblib.load("backend/rl_model/rl_duration_predictor.pkl")

# Logs file
LOG_FILE = Path("backend/traffic_log.json")
if not LOG_FILE.exists():
    LOG_FILE.write_text(json.dumps([]))

# --- 1. Video stream endpoint (kept same, optional for demo) ---
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


# --- 2 & 3. Use Simulator for Detections & Traffic Light ---
traffic_gen = generate_live_traffic(choose_road_to_open, predict_duration)

@app.get("/api/detections")
def get_detections():
    data = next(traffic_gen)
    return data["road_counts"]

@app.get("/api/traffic-light")
def get_traffic_light():
    data = next(traffic_gen)

    # Save log entry
    log_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": f"Green to {data['green_road']} for {data['duration']}s (settling {data['settling_time']}s, yellow {data['yellow_time']}s)"
    }
    logs = json.loads(LOG_FILE.read_text())
    logs.insert(0, log_entry)
    LOG_FILE.write_text(json.dumps(logs[:50]))

    return {
        "green": data["green_road"],
        "duration": data["duration"],
        "settling_time": data["settling_time"],
        "yellow_time": data["yellow_time"],
        "states": {
            "north": "green" if data["green_road"] == "north" else "red",
            "east": "green" if data["green_road"] == "east" else "red",
            "south": "green" if data["green_road"] == "south" else "red",
            "west": "green" if data["green_road"] == "west" else "red",
        }
    }


# --- 4. View logs ---
@app.get("/api/logs")
def get_logs():
    logs = json.loads(LOG_FILE.read_text())
    return {"logs": logs}


# --- 5. Summary stats ---
@app.get("/api/stats")
def get_stats():
    logs = json.loads(LOG_FILE.read_text())

    # Store waiting times for each road
    wait_times = {"north": [], "east": [], "south": [], "west": []}
    last_green_time = {"north": None, "east": None, "south": None, "west": None}

    # Replay logs to estimate wait times
    for entry in reversed(logs):  # oldest first
        event = entry["event"]
        if "Green to" in event:
            parts = event.split()
            road = parts[2]  # e.g., "north"
            duration = int(parts[4].replace("s", ""))

            # Add settling + yellow times if present
            extra_time = 0
            if "settling" in event:
                extra_time += int(event.split("settling")[1].split("s")[0].strip())
            if "yellow" in event:
                extra_time += int(event.split("yellow")[1].split("s")[0].strip())

            total_green_time = duration + extra_time

            # For other roads, this time contributes to their waiting
            for r in wait_times.keys():
                if r != road:
                    wait_times[r].append(total_green_time)

            # Reset wait for green road
            last_green_time[road] = 0

    # Compute averages
    avg_wait = {r: round(np.mean(times), 2) if times else 0 for r, times in wait_times.items()}
    total_vehicles = sum(avg_wait.values())  # proxy metric

    return {
        "total_vehicles": total_vehicles,
        "average_wait_time": avg_wait
    }

