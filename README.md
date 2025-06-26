# 🚦 Traffic Signal Timing Optimization using AI

This project is a smart traffic control system designed to dynamically optimize signal timings at a four-way intersection using live vehicle detections, contextual data (weather and holidays), and a Reinforcement Learning (RL) model.

## 📌 Project Overview

### 🎯 Goal
To reduce traffic congestion and average wait time by making data-driven decisions about which road should receive the green signal, and for how long.

---

## ✅ Features Implemented

### 🔍 Real-Time Vehicle Detection
- YOLOv8 integration for object detection (currently integrated but not fully activated due to video processing limitations).

### 🧠 Reinforcement Learning Model
- Trained Q-learning agent (`q_table.pkl`) for optimizing green light durations.
- Takes into account:
  - Number of vehicles per road
  - Weather conditions (via OpenWeatherMap API)
  - Public holidays/festivals (via Google Calendar API)

### 🧭 Contextual Awareness
- Weather: Rain or clear weather affects traffic flow.
- Holidays: Traffic expected to increase on special days.
- Time of day: Morning/evening rush hours handled differently.

### 🌐 Fullstack Dashboard
- **Frontend (HTML/CSS/JS)** for:
  - Live feeds from 4 directions (North, East, South, West)
  - Traffic light state viewer
  - Vehicle counts and signal duration
  - Logs and summary stats

- **Backend (FastAPI)** for:
  - Serving detection counts
  - Making RL decisions on green light direction and duration
  - Logging and statistics

---

## ⚙️ Project Structure

