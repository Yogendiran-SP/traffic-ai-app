import cv2
import numpy as np
from shapely.geometry import Point, Polygon

# Adding Weights for vehicles
VEHICLE_WEIGHTS = {
    "car": 1.0,
    "motorcycle": 0.3,
    "bus": 2.5,
    "truck": 3.0,
    "bicylce": 0.2,
    "auto rickshaw": 0.9
}

# Define Polygon regions for road entry areas
road_regions = {
    "north":[(100,50), (250,50), (250,150), (100,150)],
    "east":[(500,100), (600,100), (600,300), (500,300)],
    "south":[(100,400), (250,400), (250,500), (100,500)],
    "west":[(50,100), (150,100), (150,300), (50,300)]
}

# from now on this is not needed 👇
def count_vehicles_by_road(detections, region):
    count = 0
    for x1,y1,x2,y2 in detections:
        cx,cy = int((x1+x2)/2), int((y1+y2)/2)
        if Polygon(region).contains(Point(cx,cy)):
            count +=1
    return count

def count_weighted_vehicles(boxes, model, region):
    count = 0.0
    polygon = Polygon(region)
    for box in boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        if label not in VEHICLE_WEIGHTS:
            continue # Skip unknown vehicles
        x1, y1, x2, y2 = box.xyxy[0]
        center = Point((x1+x2)/2,(y1+y2)/2)
        if polygon.contains(center):
            count+=VEHICLE_WEIGHTS[label]
    return round(count, 2)

def process_frame(frame, model, road_name):
    results = model(frame)[0]
    boxes = results.boxes
    region = road_regions[road_name]
    
    count = count_weighted_vehicles(boxes, model, region)

    for box in results.boxes:
        cls = int(box.cls[0])
        label = model.names[cls]
        if label not in VEHICLE_WEIGHTS:
            continue
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, f"ID:{cls}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Draw region and count
    cv2.polylines(frame, [np.array(region, np.int32)], True, (0, 255, 0), 2)
    
    
    return frame, count