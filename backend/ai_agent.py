import joblib
import numpy as np
import os

# Load Q-table
q_table_path = "./rl_model/q_table.pkl"
if os.path.exists(q_table_path):
    Q_table = joblib.load(q_table_path)
else:
    Q_table = np.zeros((10000, 4))  # fallback if not trained yet

def encode_state(road_counts):
    """Converts vehicle counts into a state index (0–9999)"""
    north = min(int(road_counts.get('north', 0)), 9)
    east = min(int(road_counts.get('east', 0)), 9)
    south = min(int(road_counts.get('south', 0)), 9)
    west = min(int(road_counts.get('west', 0)), 9)
    return north * 1000 + east * 100 + south * 10 + west

def choose_road_to_open(road_counts):
    state = encode_state(road_counts)
    action = np.argmax(Q_table[state])  # best road index
    roads = ['north', 'east', 'south', 'west']
    return roads[action]
