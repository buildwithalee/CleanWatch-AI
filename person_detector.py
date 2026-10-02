import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolo11n.pt")

# Open laptop webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()

print("CleanWatch AI started...")
print("Press Q to stop.")

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read camera frame.")
        break

    # Run AI detection
    results = model(frame, verbose=False)

    # Draw detected objects
    annotated_frame = results[0].plot()

    # Check detections
    for box in results[0].boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        object_name = model.names[class_id]

        if object_name == "person":
            cv2.putText(
                annotated_frame,
                f"PERSON DETECTED {confidence:.0%}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

    cv2.imshow("CleanWatch AI - Live Vision", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()