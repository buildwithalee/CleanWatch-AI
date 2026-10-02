import cv2
from ultralytics import YOLO
from datetime import datetime

model = YOLO("yolo11n.pt")

camera = cv2.VideoCapture(0)

# Objects useful for our waste prototype
waste_objects = [
    "bottle",
    "cup",
    "banana",
    "apple",
    "orange"
]

print("CleanWatch AI - Waste Monitoring Started")
print("Press Q to quit.")

while True:
    success, frame = camera.read()

    if not success:
        break

    results = model(frame, verbose=False)

    person_detected = False
    detected_waste = []

    for box in results[0].boxes:

        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        object_name = model.names[class_id]

        if object_name == "person" and confidence > 0.50:
            person_detected = True

        if object_name in waste_objects and confidence > 0.40:
            detected_waste.append(object_name)

    annotated_frame = results[0].plot()

    # System status
    if person_detected and detected_waste:

        status = "POSSIBLE WASTE ACTIVITY"

        cv2.putText(
            annotated_frame,
            status,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 255),
            2
        )

        cv2.putText(
            annotated_frame,
            "Waste: " + ", ".join(set(detected_waste)),
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

    elif person_detected:

        cv2.putText(
            annotated_frame,
            "PERSON MONITORING",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2
        )

    else:

        cv2.putText(
            annotated_frame,
            "AREA CLEAR",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2
        )

    # Current time
    current_time = datetime.now().strftime("%H:%M:%S")

    cv2.putText(
        annotated_frame,
        current_time,
        (20, annotated_frame.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.imshow("CleanWatch AI - Smart Monitoring", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()