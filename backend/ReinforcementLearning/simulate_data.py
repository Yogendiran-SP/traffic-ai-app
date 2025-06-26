import random
import csv
from datetime import datetime, timedelta

roads = ['north', 'east', 'south', 'west']

with open("..traffic_log.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "north", "east", "south", "west", "green_road", "duration"])
    
    time = datetime.now()
    for _ in range(200):
        counts = {road: round(random.uniform(0, 10), 2) for road in roads}
        green = max(counts, key=counts.get)
        duration = int(5 + counts[green]*1.5)

        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            counts['north'], counts['east'], counts['south'], counts['west'],
            green, duration
        ])
        time += timedelta(minutes=5)
