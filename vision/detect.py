import cv2
from ultralytics import YOLO
model = YOLO("yolov8n.pt")

video_path = "CAM 1.mp4"
cap = cv2.VideoCapture(video_path)

print("Starting video stream... Press 'q' to close the window.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("End of video stream.")
        break

    results = model(frame, classes=[0], conf=0.4)

    annotated_frame = results[0].plot()

    cv2.imshow("AuraTrack - Vision Test", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
