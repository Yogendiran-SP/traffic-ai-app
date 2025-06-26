
# 🚦 Traffic Signal Timing Optimization using AI

A smart traffic management system that utilizes AI (Reinforcement Learning + YOLOv8 + Contextual Data) to optimize signal timing in real-time across a four-way intersection.

🔗 **Live Demo (Render.com):** [https://traffic-ai-app.onrender.com](https://traffic-ai-app.onrender.com)

---

## 📌 Project Overview

This project is an intelligent traffic signal controller that:
- Detects vehicles using **YOLOv8** object detection.
- Makes decisions using a **Q-learning Reinforcement Learning agent**.
- Considers **contextual data** such as:
  - Live **weather conditions**
  - **Festival/holiday schedules** (via Google Calendar API)
- Simulates real-time video feeds for **North, South, East, and West** roads.
- Displays output through a **web-based dashboard** built with HTML, CSS, and JavaScript.

---

## ✅ Features Implemented So Far

- [x] FastAPI backend with modular design
- [x] Reinforcement Learning agent training using Q-learning
- [x] YOLOv8-based traffic detection pipeline
- [x] Festival/holiday integration using Google Calendar API
- [x] Weather condition integration using OpenWeatherMap API
- [x] Frontend dashboard with vehicle count, live feeds, and traffic light state
- [x] API endpoints for live updates, stats, and logs

---

## 🚧 Current Status

> The live vehicle detection from videos is still in development. The dashboard interface is functional, but real-time traffic stats are yet to fully integrate due to some API errors (502/404).

✅ Over **50%** functionality has been implemented, with future work planned for:
- Full YOLOv8 inference from webcam or video feed
- Real-time vehicle stats updates
- End-to-end signal control using AI prediction

---

## 📁 Project Structure

```bash
traffic-ai-app/
├── backend/
│   ├── app.py                  # FastAPI entrypoint
│   ├── ai_agent.py             # Traffic decision logic using RL
│   ├── trafficenv.py           # RL Environment definition
│   ├── logger.py               # Logging system for actions and stats
│   ├── camera_streams.py       # Simulated camera handling (in progress)
│   ├── holiday_data/
│   │   ├── holiday_fetcher.py, token utils...
│   ├── weather_api.py          # Weather API integration
│   ├── ReinforcementLearning/
│   │   ├── q_learning_agent.py, train_q_learning.py, etc.
│   ├── rl_model/
│   │   ├── q_table.pkl, rl_duration_predictor.pkl
│   ├── yolov8_model/
│   │   ├── traffic_detector.py, yolov8n.pt
│   └── traffic_log.csv         # Runtime vehicle + light data
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── styles.css
│
├── data/
│   ├── north.mp4, south.mp4, etc.  # Simulated feeds
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/traffic-ai-app.git
cd traffic-ai-app
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the FastAPI Backend
```bash
cd backend
uvicorn app:app --reload
```

### 5. Open the Frontend
Navigate to `/frontend/index.html` in your browser, or serve it using a local server (like Live Server in VSCode).

---

## 🧠 AI & ML Components

- **Q-Learning Agent:** Determines the best signal timing based on traffic flow.
- **YOLOv8 Model:** Detects number of vehicles per direction.
- **Reward Shaping:** Uses context (weather, festival, time of day) to influence AI decisions.

---

## 📊 Dashboard Preview

The dashboard displays:
- Live feed from 4 roads
- Vehicle counts per road
- Traffic light state
- Stats (avg wait time, total vehicles)
- Logs of actions taken

![Dashboard Screenshot](https://traffic-ai-app.onrender.com)

---

## 🧩 APIs Used

- OpenWeatherMap API (for weather)
- Google Calendar API (for holiday detection)
- YOLOv8 (via Ultralytics)

---

## 📅 Future Work

- Integrate real YOLO detection with video streams
- Enable socket updates for live dashboard refresh
- Add charts and historical analytics to dashboard

---

## 📬 Contact

For queries or collaboration:
**Your Name**  
📧 your.email@example.com  
🔗 [LinkedIn](#) | [GitHub](#)
