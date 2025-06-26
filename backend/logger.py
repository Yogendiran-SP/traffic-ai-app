import csv
import os
from datetime import datetime

def log_traffic_data(road_counts, green_road, duration, filename="traffic_log.csv"):
    # Create one if not exist
    # if not os.path.exists(filename):
    #     with open(filename, mode="w", newline="") as file:
    #         write = csv.writer(file)
    #         write.writerow([
    #             "timestamp", "north", "east", "south", "west", "green_road", "duration"
    #         ])
        
        # Write traffic data
    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime().now().isoformat(),
            road_counts['north'],
            road_counts['east'],
            road_counts['south'],
            road_counts['west'],
            green_road,
            duration
        ])