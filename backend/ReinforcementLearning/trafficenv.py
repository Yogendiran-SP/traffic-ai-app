import numpy as np
import json
from datetime import date, datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.weather_api import get_weather_data

class TrafficEnv:
    def __init__(self):
        self.max_vehicle = 10  # Cap for discretization
        self.state = None
        self.weather_condition = None  # e.g., 'Clear', 'Rain', etc.
        self.done = False
        # Loading Holiday data
        with open("../holiday_data/upcoming_holidays.json") as f:
            self.holidays = json.load(f)

    def is_today_holiday(self):
        today = date.today().isoformat()
        return int(any(start == today for (start, _) in self.holidays))


    def reset(self):
        self.weather_condition = get_weather_data()["condition"]
        self.traffic = {
            "north": np.random.randint(0, 11),
            "east": np.random.randint(0, 11),
            "south": np.random.randint(0, 11),
            "west": np.random.randint(0, 11)
        }
        self.is_holiday = self.is_today_holiday()
        self.state = self.encode_state(self.traffic, self.is_holiday)
        self.done = False
        return self.state

    def step(self, action):
        roads = ["north", "east", "south", "west"]
        green_road = roads[action]

        wait_penalty = sum([count for road, count in self.traffic.items() if road != green_road])
        reward = 100 - wait_penalty  # Positive for clearing traffic

        # 🧠 Add weather penalty if it's rainy and vehicle count is high on green_road
        if self.weather_condition in ["Rain", "Thunderstorm"]:
            if self.traffic[green_road] > 6:
                reward -= 20  # Encourage safer decision in bad weather

        # Holiday penalty or boost
        if self.is_holiday:
            reward -= 10  # e.g., simulate holiday congestion effect

        # Reset traffic for next step
        self.traffic = {
            "north": np.random.randint(0, 11),
            "east": np.random.randint(0, 11),
            "south": np.random.randint(0, 11),
            "west": np.random.randint(0, 11)
        }

        self.is_holiday = self.is_today_holiday()
        self.state = self.encode_state(self.traffic, self.is_holiday)
        return self.state, reward, self.done

    def encode_state(self, traffic, is_holiday):
        # Encode 4-road traffic into a unique state ID
        base_state = (traffic["north"] * 1000 +
                traffic["east"] * 100 +
                traffic["south"] * 10 +
                traffic["west"])
        return base_state + (10000 * is_holiday)

    def action_space_sample(self):
        return np.random.choice([0, 1, 2, 3])
