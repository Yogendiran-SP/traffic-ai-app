import os
import random
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
from pathlib import Path
import numpy as np

# Try model imports, fallback gracefully
try:
    import joblib
    from ultralytics import YOLO
    from backend.ReinforcementLearning.simulate_data import generate_live_traffic
    from backend.ai_agent import choose_road_to_open
    from backend.logger import log_traffic_data
    from backend.ReinforcementLearning.predict import predict_duration
    MODELS_AVAILABLE = True
except Exception as e:
    print("⚠️ Running in fallback mode (no YOLO/RL):", e)
    MODELS_AVAILABLE = False

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

# Logs file
LOG_FILE = Path("backend/traffic_log.json")
if not LOG_FILE.exists():
    LOG_FILE.write_text(json.dumps([]))

# --- Models (lazy load) ---
yolo_model = None
rl_model = None

def get_yolo_model():
    global yolo_model
    if yolo_model is None and MODELS_AVAILABLE:
        yolo_model = YOLO("yolov8_model/yolov8n.pt")
    return yolo_model

def get_rl_model():
    global rl_model
    if rl_model is None and MODELS_AVAILABLE:
        rl_model = joblib.load("backend/rl_model/rl_duration_predictor.pkl")
    return rl_model

# --- 1. Detections ---
@app.get("/api/detections")
def get_detections():
    if MODELS_AVAILABLE:
        # Use simulated generator
        data = next(generate_live_traffic(choose_road_to_open, predict_duration))
        return data["road_counts"]
    else:
        # Fallback: random counts
        return {
            "north": {"vehicles": random.randint(0, 15)},
            "south": {"vehicles": random.randint(0, 15)},
            "east": {"vehicles": random.randint(0, 15)},
            "west": {"vehicles": random.randint(0, 15)},
        }

# --- 2. Traffic light decision ---
@app.get("/api/traffic-light")
def get_traffic_light():
    if MODELS_AVAILABLE:
        data = next(generate_live_traffic(choose_road_to_open, predict_duration))
        green = data["green_road"]
        duration = data["duration"]
    else:
        # Random fallback
        green = random.choice(["north", "south", "east", "west"])
        duration = random.randint(5, 20)

    state = {d: "red" for d in ["north", "south", "east", "west"]}
    state[green] = "green"

    log_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": f"Green to {green} for {duration}s"
    }
    logs = json.loads(LOG_FILE.read_text())
    logs.insert(0, log_entry)
    LOG_FILE.write_text(json.dumps(logs[:50]))

    return {"green": green, "duration": duration, "states": state}

# --- 3. Logs ---
@app.get("/api/logs")
def get_logs():
    logs = json.loads(LOG_FILE.read_text())
    return {"logs": logs}

# --- 4. Stats ---
@app.get("/api/stats")
def get_stats():
    logs = json.loads(LOG_FILE.read_text())

    # Simple average wait estimation
    wait_times = {"north": [], "south": [], "east": [], "west": []}
    for entry in logs:
        if "Green to" in entry["event"]:
            parts = entry["event"].split()
            road = parts[2]
            duration = int(parts[4].replace("s", ""))
            for r in wait_times.keys():
                if r != road:
                    wait_times[r].append(duration)

    avg_wait = {r: round(np.mean(times), 2) if times else 0 for r, times in wait_times.items()}
    total_vehicles = sum(random.randint(5, 15) for _ in wait_times)

    return {"total_vehicles": total_vehicles, "average_wait_time": avg_wait}
