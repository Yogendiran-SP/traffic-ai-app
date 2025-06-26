import cv2

def get_video_captures():
    return {
        "north": cv2.VideoCapture("../data/north.mp4"),
        "east": cv2.VideoCapture("../data/east.mp4"),
        "south": cv2.VideoCapture("../data/south.mp4"),
        "west": cv2.VideoCapture("../data/west.mp4")
    }