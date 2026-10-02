from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from agents import CleanWatchAgents
from ultralytics import YOLO
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
import json
import os
import uuid
import time


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="CleanWatch AI API",
    version="3.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "incidents.json"
)

EVIDENCE_DIR = os.path.join(
    BASE_DIR,
    "evidence"
)

os.makedirs(
    EVIDENCE_DIR,
    exist_ok=True
)
app.mount(
    "/evidence",
    StaticFiles(directory=EVIDENCE_DIR),
    name="evidence"
)

# ============================================================
# AI AGENTS
# ============================================================

agents = CleanWatchAgents()


# ============================================================
# YOLO MODEL
# ============================================================

yolo_model = YOLO(
    "yolo11n.pt"
)


# ============================================================
# WASTE-LIKE COCO OBJECTS
# ============================================================

WASTE_CLASSES = {
    "bottle",
    "cup",
    "banana",
    "apple",
    "orange",
}


# ============================================================
# DUMPING EVENT CONFIGURATION
# ============================================================

DUMP_CONFIRM_SECONDS = 2.0

INCIDENT_COOLDOWN_SECONDS = 15.0


# ============================================================
# TEMPORAL VISION STATE
# ============================================================

vision_state = {

    # Was a person recently seen together with waste?
    "person_with_waste_seen": False,

    # Time when person disappeared but waste remained
    "person_left_time": None,

    # Last automatic incident timestamp
    "last_incident_time": 0.0,

    # Current event phase
    "event_phase": "MONITORING"
}


# ============================================================
# INCIDENT HELPERS
# ============================================================

def load_incidents():

    if not os.path.exists(DATA_FILE):
        return []

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as error:

        print(
            "Incident loading error:",
            error
        )

        return []


def save_incidents(data):

    try:

        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    except Exception as error:

        print(
            "Incident saving error:",
            error
        )


# ============================================================
# SAVE EVIDENCE IMAGE
# ============================================================

def save_evidence_image(frame):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"incident_{timestamp}.jpg"
    )

    filepath = os.path.join(
        EVIDENCE_DIR,
        filename
    )

    cv2.imwrite(
        filepath,
        frame
    )

    return filename


# ============================================================
# AUTOMATIC INCIDENT CREATION
# ============================================================

def create_ai_incident(
    waste_type,
    location,
    confidence,
    evidence_file=None
):

    incidents = load_incidents()


    # --------------------------------------------------------
    # CLEAN VALUES
    # --------------------------------------------------------

    if not waste_type:

        waste_type = "Unknown Waste"


    formatted_waste = (
        waste_type
        .replace("_", " ")
        .title()
    )


    confidence_value = int(
        round(confidence)
    )


    # --------------------------------------------------------
    # RUN MULTI-AGENT AI PIPELINE
    # --------------------------------------------------------

    analysis = agents.run(
        formatted_waste,
        location,
        confidence_value
    )


    # --------------------------------------------------------
    # CREATE INCIDENT
    # --------------------------------------------------------

    incident = {

        "id":
            f"CW-{str(uuid.uuid4())[:6].upper()}",

        "waste_type":
            formatted_waste,

        "location":
            location,

        "severity":
            analysis["severity"],

        "status":
            "AI Investigated",

        "confidence":
            confidence_value,

        "timestamp":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "ai_summary":
            analysis["summary"],

        "recommended_action":
            analysis["recommended_action"],

        "agent_trace":
            analysis["agents_executed"],

        "ai_engine":
            analysis["ai_engine"],

        "evidence_file":
            evidence_file,

        "detection_source":
            "YOLO11 Live Vision",

        "event_type":
            "Possible Waste Dumping"
    }


    incidents.insert(
        0,
        incident
    )


    save_incidents(
        incidents
    )


    print(
        f"Automatic incident created: {incident['id']}"
    )


    return incident


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {

        "system":
            "CleanWatch AI",

        "version":
            "3.0",

        "status":
            "online",

        "vision_engine":
            "YOLO11",

        "investigation_engine":
            "Google Gemini",

        "pipeline": [
            "Browser Camera",
            "YOLO11 Vision",
            "Temporal Event Detection",
            "Evidence Agent",
            "Severity Agent",
            "Gemini Investigation Agent",
            "Response Agent",
            "Human Review"
        ]
    }


# ============================================================
# LIVE FRAME DETECTION
# ============================================================

@app.post("/detect-frame")
async def detect_frame(
    file: UploadFile = File(...)
):

    try:

        # ----------------------------------------------------
        # READ BROWSER IMAGE
        # ----------------------------------------------------

        contents = await file.read()


        image_array = np.frombuffer(
            contents,
            np.uint8
        )


        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )


        if frame is None:

            return {
                "success": False,
                "error": "Invalid image received"
            }


        # ----------------------------------------------------
        # YOLO INFERENCE
        # ----------------------------------------------------

        results = yolo_model(
            frame,
            verbose=False
        )


        detections = []

        person_detected = False

        waste_detected = False

        detected_waste = None

        highest_waste_confidence = 0.0


        # ----------------------------------------------------
        # PROCESS DETECTIONS
        # ----------------------------------------------------

        for result in results:

            for box in result.boxes:

                class_id = int(
                    box.cls[0]
                )


                confidence = float(
                    box.conf[0]
                )


                class_name = (
                    yolo_model.names[
                        class_id
                    ]
                )


                confidence_percent = round(
                    confidence * 100,
                    2
                )


                detections.append({

                    "class":
                        class_name,

                    "confidence":
                        confidence_percent
                })


                # PERSON

                if class_name == "person":

                    person_detected = True


                # WASTE

                if class_name in WASTE_CLASSES:

                    waste_detected = True


                    if (
                        confidence_percent
                        >
                        highest_waste_confidence
                    ):

                        highest_waste_confidence = (
                            confidence_percent
                        )

                        detected_waste = (
                            class_name
                        )


        # ====================================================
        # BASIC VISION STATUS
        # ====================================================

        if (
            person_detected
            and
            waste_detected
        ):

            status = (
                "PERSON_WITH_WASTE"
            )


        elif waste_detected:

            status = (
                "WASTE_DETECTED"
            )


        elif person_detected:

            status = (
                "PERSON_DETECTED"
            )


        else:

            status = "CLEAR"


        # ====================================================
        # TEMPORAL DUMPING EVENT LOGIC
        # ====================================================

        current_time = time.time()

        dumping_event = False

        automatic_incident = None


        # ----------------------------------------------------
        # STAGE 1
        # Person and waste seen together
        # ----------------------------------------------------

        if (
            person_detected
            and
            waste_detected
        ):

            vision_state[
                "person_with_waste_seen"
            ] = True


            vision_state[
                "person_left_time"
            ] = None


            vision_state[
                "event_phase"
            ] = "PERSON_WITH_WASTE"


        # ----------------------------------------------------
        # STAGE 2
        # Person disappears but waste remains
        # ----------------------------------------------------

        elif (
            not person_detected
            and
            waste_detected
            and
            vision_state[
                "person_with_waste_seen"
            ]
        ):

            if (
                vision_state[
                    "person_left_time"
                ]
                is None
            ):

                vision_state[
                    "person_left_time"
                ] = current_time


                vision_state[
                    "event_phase"
                ] = "VERIFYING_DUMPING"


            elapsed = (
                current_time
                -
                vision_state[
                    "person_left_time"
                ]
            )


            # ------------------------------------------------
            # STAGE 3
            # Waste remained after person left
            # ------------------------------------------------

            if (
                elapsed
                >=
                DUMP_CONFIRM_SECONDS
            ):

                cooldown_elapsed = (
                    current_time
                    -
                    vision_state[
                        "last_incident_time"
                    ]
                )


                if (
                    cooldown_elapsed
                    >=
                    INCIDENT_COOLDOWN_SECONDS
                ):

                    dumping_event = True


                    vision_state[
                        "event_phase"
                    ] = "DUMPING_EVENT"


                    # ----------------------------------------
                    # SAVE EVIDENCE
                    # ----------------------------------------

                    evidence_file = (
                        save_evidence_image(
                            frame
                        )
                    )


                    # ----------------------------------------
                    # RUN GEMINI + AGENTS
                    # ----------------------------------------

                    automatic_incident = (
                        create_ai_incident(
                            waste_type=(
                                detected_waste
                                or
                                "Unknown Waste"
                            ),
                            location=(
                                "Camera 01 - Demo Zone"
                            ),
                            confidence=(
                                highest_waste_confidence
                            ),
                            evidence_file=(
                                evidence_file
                            )
                        )
                    )


                    vision_state[
                        "last_incident_time"
                    ] = current_time


                    # Reset event sequence

                    vision_state[
                        "person_with_waste_seen"
                    ] = False


                    vision_state[
                        "person_left_time"
                    ] = None


        # ----------------------------------------------------
        # NO WASTE
        # Reset pending event after person leaves with object
        # ----------------------------------------------------

        elif not waste_detected:

            vision_state[
                "person_left_time"
            ] = None


            if not person_detected:

                vision_state[
                    "person_with_waste_seen"
                ] = False


                vision_state[
                    "event_phase"
                ] = "MONITORING"


        # ====================================================
        # RESPONSE TO FRONTEND
        # ====================================================

        return {

            "success":
                True,

            "status":
                status,

            "person_detected":
                person_detected,

            "waste_detected":
                waste_detected,

            "waste_type":
                detected_waste,

            "confidence":
                highest_waste_confidence,

            "detections":
                detections,

            "event_phase":
                vision_state[
                    "event_phase"
                ],

            "dumping_event":
                dumping_event,

            "incident_created":
                automatic_incident
                is not None,

            "incident":
                automatic_incident
        }


    except Exception as error:

        print(
            "Frame detection error:",
            error
        )


        return {

            "success":
                False,

            "error":
                str(error)
        }


# ============================================================
# GET INCIDENTS
# ============================================================

@app.get("/incidents")
def get_incidents():

    return load_incidents()


# ============================================================
# MANUAL / DEMO INCIDENT
# ============================================================

@app.post("/incidents")
def create_incident(
    waste_type: str = "Plastic Bottle",
    location: str = "Camera 01 - Demo Zone",
    confidence: int = 91
):

    return create_ai_incident(
        waste_type=waste_type,
        location=location,
        confidence=confidence,
        evidence_file=None
    )


# ============================================================
# INCIDENT DETAILS
# ============================================================

@app.get("/incidents/{incident_id}")
def incident_details(
    incident_id: str
):

    incidents = load_incidents()


    for incident in incidents:

        if (
            incident["id"]
            ==
            incident_id
        ):

            return incident


    return {
        "error":
            "Incident not found"
    }


# ============================================================
# ANALYTICS
# ============================================================

@app.get("/analytics")
def analytics():

    incidents = load_incidents()


    return {

        "total_incidents":
            len(incidents),

        "high_priority":
            len([
                incident
                for incident in incidents
                if incident.get(
                    "severity"
                ) == "High"
            ]),

        "medium_priority":
            len([
                incident
                for incident in incidents
                if incident.get(
                    "severity"
                ) == "Medium"
            ]),

        "low_priority":
            len([
                incident
                for incident in incidents
                if incident.get(
                    "severity"
                ) == "Low"
            ]),

        "ai_investigated":
            len([
                incident
                for incident in incidents
                if incident.get(
                    "status"
                )
                ==
                "AI Investigated"
            ]),

        "resolved":
            len([
                incident
                for incident in incidents
                if incident.get(
                    "status"
                )
                ==
                "Resolved"
            ])
    }


# ============================================================
# RESOLVE INCIDENT
# ============================================================

@app.patch(
    "/incidents/{incident_id}/resolve"
)
def resolve_incident(
    incident_id: str
):

    incidents = load_incidents()


    for incident in incidents:

        if (
            incident["id"]
            ==
            incident_id
        ):

            incident[
                "status"
            ] = "Resolved"


            incident[
                "resolved_at"
            ] = (
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )


            save_incidents(
                incidents
            )


            return {

                "message":
                    "Incident resolved",

                "incident":
                    incident
            }


    return {
        "error":
            "Incident not found"
    }


# ============================================================
# RESET VISION STATE
# Useful during hackathon demo/testing
# ============================================================

@app.post("/vision/reset")
def reset_vision_state():

    vision_state[
        "person_with_waste_seen"
    ] = False

    vision_state[
        "person_left_time"
    ] = None

    vision_state[
        "last_incident_time"
    ] = 0.0

    vision_state[
        "event_phase"
    ] = "MONITORING"


    return {
        "message":
            "Vision state reset",

        "status":
            "ready"
    }