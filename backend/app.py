import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import cv2
from pathlib import Path
import joblib
from datetime import datetime
import numpy as np
from ultralytics import YOLO

from .camera_streams import get_video_captures
from ai_agent import choose_road_to_open
from logger import log_traffic_data
from yolov8_model.traffic_detector import process_frame
from ReinforcementLearning.predict import predict_duration

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend)
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

# Loading  models
yolo_model = YOLO("./yolov8_model/yolov8n.pt") # 'n' is nano (small,fast), you can also use 'm' or'l' for better accuracy
rl_model = joblib.load("backend/ml_model/model.pkl")

# Load video
caps = get_video_captures()

# --- API Endpoints ---

# 1. Video streaming endpoint (sample, one direction)
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

# 2. Detections endpoint (mock)
@app.get("/api/detections")
def get_detections():
    # Replace with real detection logic
    return {
        "north": {"vehicles": 5},
        "south": {"vehicles": 3},
        "east": {"vehicles": 7},
        "west": {"vehicles": 2},
    }

# 3. Traffic light state endpoint (mock)
@app.get("/api/traffic-light")
def get_traffic_light():
    # Replace with real AI logic
    return {
        "green": "north",
        "duration": 30,
        "states": {
            "north": "green",
            "south": "red",
            "east": "red",
            "west": "red"
        }
    }

# 4. Logs endpoint (mock)
@app.get("/api/logs")
def get_logs():
    # Replace with real log reading
    return {
        "logs": [
            {"time": "2024-06-25 10:00:00", "event": "Green to north for 30s"},
            {"time": "2024-06-25 09:59:30", "event": "Green to east for 25s"},
        ]
    }

# 5. Stats endpoint (mock)
@app.get("/api/stats")
def get_stats():
    # Replace with real stats
    return {
        "total_vehicles": 17,
        "average_wait_time": 12.5
    }

while True:
    road_counts = {}
    processed_frames = {} 

    for road, cap in caps.items():
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.resize(frame, (640, 480))
        # Process each frame
        processed, count = process_frame(frame, yolo_model, road)
        processed_frames[road] = processed
        road_counts[road] = count

    # AI selects road for green signal
    green_road = choose_road_to_open(road_counts)
    green_duration = predict_duration(road_counts, green_road)
    log_traffic_data(road_counts, green_road, green_duration)
    print("Vehicle Counts:", road_counts)
    print("Green Signal to:", green_road)

    now = datetime.now()


    # Display all frames
    for road, frame in processed_frames.items():
        label = f"{road.upper()} [GREEN]" if road == green_road else road.upper()
        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if road == green_road else (0, 0, 255), 2)
        cv2.imshow(road, frame)

    if cv2.waitKey(1) & (0xFF) == ord('q'):
        break

for cap in caps.values():
    cap.release()
cv2.destroyAllWindows()