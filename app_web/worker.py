# worker.py
import cv2
import time
from ultralytics import YOLO
from state import latest_frame, estado

RTSP_URL = "rtsp://admin:Novat3ch@192.168.137.35:554/Streaming/Channels/101"
MODEL_PATH = "static/model/best.pt"

def run_worker():
    global latest_frame, estado

    model = YOLO(MODEL_PATH)
    cap = cv2.VideoCapture(RTSP_URL)

    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(1)
            continue

        frame_id += 1

        if frame_id % 5 == 0:
            results = model(frame, conf=0.5)
            boxes = results[0].boxes

            atentos = 0
            total = len(boxes)

            for box in boxes:
                cls = int(box.cls[0])
                label = model.names[cls]
                if label.lower() == "atento":
                    atentos += 1

            estado["nivel"] = atentos / total if total else 0

        latest_frame = frame
        time.sleep(0.03)
