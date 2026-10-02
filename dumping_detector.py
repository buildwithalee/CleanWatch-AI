import cv2
import os
import time
import requests
from datetime import datetime
from ultralytics import YOLO

# ==========================================
# CLEANWATCH AI - REAL-TIME VISION MODULE
# ==========================================

model = YOLO("yolo11n.pt")

camera = cv2.VideoCapture(0)

API_URL = "http://127.0.0.1:8000/incidents"

EVIDENCE_FOLDER = "evidence"

os.makedirs(EVIDENCE_FOLDER, exist_ok=True)

WASTE_OBJECTS = [
    "bottle",
    "cup",
    "banana",
    "apple",
    "orange"
]

PERSON_CONFIDENCE = 0.50
WASTE_CONFIDENCE = 0.30

DUMP_WAIT_TIME = 2.0
EVENT_COOLDOWN = 10

person_with_waste_seen = False
person_missing_start = None

last_event_time = 0
last_waste_name = "Unknown"
last_confidence = 0


def send_incident_to_ai(
    waste_type,
    confidence
):
    """
    Send detected incident to CleanWatch backend.
    Backend agents will investigate it.
    """

    try:

        params = {
            "waste_type": waste_type,
            "location": "Camera 01 - Demo Zone",
            "confidence": int(confidence * 100)
        }

        response = requests.post(
            API_URL,
            params=params,
            timeout=5
        )

        if response.status_code == 200:

            incident = response.json()

            print("")
            print("====================================")
            print("AGENTIC AI INVESTIGATION COMPLETE")
            print("Incident:", incident["id"])
            print("Severity:", incident["severity"])
            print("AI:", incident["ai_summary"])
            print(
                "Action:",
                incident["recommended_action"]
            )
            print("====================================")
            print("")

        else:

            print(
                "Backend error:",
                response.status_code
            )

    except Exception as error:

        print(
            "Could not contact backend:",
            error
        )


print("")
print("====================================")
print(" CLEANWATCH AI")
print(" REAL-TIME SMART MONITORING")
print("====================================")
print("")
print("Vision Engine: ONLINE")
print("Agentic Backend: READY")
print("")
print("Press Q to quit.")
print("")


while True:

    success, frame = camera.read()

    if not success:
        break

    now = time.time()

    results = model(
        frame,
        verbose=False
    )

    person_detected = False
    waste_detected = False

    waste_name = None
    waste_confidence = 0


    # ==================================
    # DETECTION
    # ==================================

    for box in results[0].boxes:

        class_id = int(
            box.cls[0]
        )

        confidence = float(
            box.conf[0]
        )

        object_name = model.names[
            class_id
        ]


        if (
            object_name == "person"
            and
            confidence >= PERSON_CONFIDENCE
        ):

            person_detected = True


        if (
            object_name in WASTE_OBJECTS
            and
            confidence >= WASTE_CONFIDENCE
        ):

            waste_detected = True

            waste_name = object_name

            waste_confidence = confidence

            last_waste_name = object_name

            last_confidence = confidence


    # ==================================
    # PERSON + WASTE
    # ==================================

    if (
        person_detected
        and
        waste_detected
    ):

        person_with_waste_seen = True

        person_missing_start = None

        status = (
            "PERSON WITH WASTE DETECTED"
        )

        color = (
            0,
            255,
            255
        )


    # ==================================
    # POSSIBLE DUMPING
    # ==================================

    elif (
        person_with_waste_seen
        and
        not person_detected
        and
        waste_detected
    ):

        if person_missing_start is None:

            person_missing_start = now

            print(
                "Possible event detected..."
            )


        elapsed = (
            now -
            person_missing_start
        )


        if elapsed >= DUMP_WAIT_TIME:

            status = (
                "POSSIBLE DUMPING EVENT"
            )

            color = (
                0,
                0,
                255
            )


            if (
                now - last_event_time
                >= EVENT_COOLDOWN
            ):

                timestamp = (
                    datetime.now()
                    .strftime(
                        "%Y%m%d_%H%M%S"
                    )
                )


                filename = os.path.join(
                    EVIDENCE_FOLDER,
                    f"incident_{timestamp}.jpg"
                )


                # Save evidence

                cv2.imwrite(
                    filename,
                    frame
                )


                print("")
                print(
                    "DUMPING EVENT DETECTED"
                )
                print(
                    "Waste:",
                    last_waste_name
                )
                print(
                    "Evidence:",
                    filename
                )


                # Send to AI agents

                send_incident_to_ai(
                    last_waste_name.title(),
                    last_confidence
                )


                last_event_time = now

                person_with_waste_seen = False

                person_missing_start = None


        else:

            status = (
                f"INVESTIGATING... "
                f"{elapsed:.1f}s"
            )

            color = (
                0,
                165,
                255
            )


    # ==================================
    # OTHER STATES
    # ==================================

    elif person_detected:

        status = "PERSON MONITORING"

        color = (
            0,
            255,
            0
        )


    elif waste_detected:

        status = (
            f"WASTE DETECTED: "
            f"{waste_name.upper()}"
        )

        color = (
            255,
            0,
            255
        )


    else:

        status = "AREA CLEAR"

        color = (
            255,
            255,
            255
        )


    # ==================================
    # DISPLAY
    # ==================================

    annotated = results[0].plot()


    cv2.rectangle(
        annotated,
        (10, 10),
        (620, 65),
        (0, 0, 0),
        -1
    )


    cv2.putText(
        annotated,
        status,
        (20, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        color,
        2
    )


    current_time = (
        datetime.now()
        .strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


    cv2.putText(
        annotated,
        current_time,
        (
            20,
            annotated.shape[0] - 20
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (
            255,
            255,
            255
        ),
        2
    )


    cv2.imshow(
        "CleanWatch AI - Live Vision",
        annotated
    )


    if (
        cv2.waitKey(1)
        & 0xFF
        == ord("q")
    ):

        break


camera.release()

cv2.destroyAllWindows()