from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from agents import CleanWatchAgents
import json
import os
import uuid


app = FastAPI(
    title="CleanWatch AI API",
    version="2.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATA_FILE = os.path.join(
    os.path.dirname(__file__),
    "incidents.json"
)


agents = CleanWatchAgents()


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

    except:

        return []


def save_incidents(data):

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


@app.get("/")
def home():

    return {
        "system": "CleanWatch AI",
        "version": "2.0",
        "status": "online",

        "pipeline": [
            "Computer Vision",
            "Evidence Agent",
            "Severity Agent",
            "Investigation Agent",
            "Response Agent"
        ]
    }


@app.get("/incidents")
def get_incidents():

    return load_incidents()


@app.post("/incidents")
def create_incident(
    waste_type: str = "Plastic Bottle",
    location: str = "Main Gate",
    confidence: int = 91
):

    incidents = load_incidents()


    # ----------------------------
    # RUN AGENTIC PIPELINE
    # ----------------------------

    analysis = agents.run(
        waste_type,
        location,
        confidence
    )


    incident = {

        "id":
            f"CW-{str(uuid.uuid4())[:6].upper()}",

        "waste_type":
            waste_type,

        "location":
            location,

        "severity":
            analysis["severity"],

        "status":
            "AI Investigated",

        "confidence":
            confidence,

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
    analysis["ai_engine"]
    }


    incidents.insert(
        0,
        incident
    )


    save_incidents(
        incidents
    )


    return incident


@app.get("/incidents/{incident_id}")
def incident_details(
    incident_id: str
):

    incidents = load_incidents()

    for incident in incidents:

        if incident["id"] == incident_id:

            return incident

    return {
        "error":
            "Incident not found"
    }


@app.get("/analytics")
def analytics():

    incidents = load_incidents()

    return {

        "total_incidents":
            len(incidents),

        "high_priority":
            len([
                i for i in incidents
                if i["severity"] == "High"
            ]),

        "medium_priority":
            len([
                i for i in incidents
                if i["severity"] == "Medium"
            ]),

        "low_priority":
            len([
                i for i in incidents
                if i["severity"] == "Low"
            ]),

        "ai_investigated":
            len([
                i for i in incidents
                if i["status"] == "AI Investigated"
            ])
    }

@app.patch("/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: str):

    incidents = load_incidents()

    for incident in incidents:

        if incident["id"] == incident_id:

            incident["status"] = "Resolved"

            incident["resolved_at"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            save_incidents(incidents)

            return {
                "message": "Incident resolved",
                "incident": incident
            }

    return {
        "error": "Incident not found"
    }