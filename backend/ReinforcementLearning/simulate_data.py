# backend/simulator.py
import random
import time

class TrafficSimulator:
    def __init__(self):
        self.roads = {"north": 0, "east": 0, "south": 0, "west": 0}

    def step(self, green_road, duration):
        # 1. Vehicles arrive (all roads)
        arrivals = {road: random.randint(0, 3) for road in self.roads}
        for road in self.roads:
            self.roads[road] += arrivals[road]

        # 2. Settling time → 1-2 sec no vehicles leave
        settling_time = random.randint(1, 2)
        effective_duration = max(0, duration - settling_time)

        # 3. Vehicles leave during effective green
        leaving = min(self.roads[green_road], random.randint(1, 2) * effective_duration)
        self.roads[green_road] -= leaving

        # 4. Yellow clearance time
        yellow_time = 2  # fixed
        total_cycle_time = duration + yellow_time

        return self.roads.copy(), total_cycle_time, settling_time, yellow_time


# Generator for continuous live traffic
def generate_live_traffic(choose_road_to_open, predict_duration):
    simulator = TrafficSimulator()
    while True:
        green_road = choose_road_to_open(simulator.roads)
        duration = predict_duration(simulator.roads, green_road)

        state, cycle_time, settle, yellow = simulator.step(green_road, duration)

        yield {
            "road_counts": state,
            "green_road": green_road,
            "duration": duration,
            "settling_time": settle,
            "yellow_time": yellow
        }

        time.sleep(cycle_time)  # includes green + yellow
