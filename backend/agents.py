import os
import json
from datetime import datetime
from dotenv import load_dotenv
from google import genai

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class CleanWatchAgents:

    def __init__(self):

        self.client = None

        if GEMINI_API_KEY:
            try:
                self.client = genai.Client(
                    api_key=GEMINI_API_KEY
                )
            except Exception as error:
                print("Gemini initialization failed:", error)


    # ==========================================
    # AGENT 1 - EVIDENCE AGENT
    # ==========================================

    def evidence_agent(
        self,
        waste_type,
        location,
        confidence
    ):

        return {
            "agent": "Evidence Agent",
            "result": (
                f"{waste_type} activity detected at "
                f"{location} with {confidence}% "
                f"computer-vision confidence."
            )
        }


    # ==========================================
    # AGENT 2 - SEVERITY AGENT
    # ==========================================

    def severity_agent(
        self,
        confidence
    ):

        if confidence >= 85:
            severity = "High"

        elif confidence >= 60:
            severity = "Medium"

        else:
            severity = "Low"


        return {
            "agent": "Severity Agent",
            "severity": severity,
            "reason": (
                f"Initial severity classified as "
                f"{severity} from detection confidence."
            )
        }


    # ==========================================
    # AGENT 3 - GEMINI INVESTIGATION AGENT
    # ==========================================

    def investigation_agent(
        self,
        waste_type,
        location,
        confidence,
        severity
    ):

        fallback_summary = (
            f"A possible waste disposal event involving "
            f"{waste_type} was detected at {location}. "
            f"Computer vision confidence was {confidence}%."
        )


        # If Gemini unavailable → safe fallback

        if not self.client:

            return {
                "agent": "Gemini Investigation Agent",
                "summary": fallback_summary,
                "source": "Local Fallback"
            }


        prompt = f"""
You are the Investigation Agent inside CleanWatch AI,
an intelligent waste-monitoring system.

Computer vision produced the following event:

Waste object: {waste_type}
Location: {location}
Detection confidence: {confidence}%
Initial severity: {severity}

Your task:

1. Analyze the event conservatively.
2. Do not claim illegal dumping as certain.
3. Mention that this is a possible waste-disposal event.
4. Produce a short professional assessment.
5. Keep the response under 70 words.
6. Do not use markdown.

Return only the assessment.
"""


        try:

            response = self.client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )

            summary = response.text.strip()

            return {
                "agent": "Gemini Investigation Agent",
                "summary": summary,
                "source": "Google Gemini"
            }


        except Exception as error:

            print(
                "Gemini investigation failed. "
                "Using fallback:",
                error
            )

            return {
                "agent": "Gemini Investigation Agent",
                "summary": fallback_summary,
                "source": "Local Fallback"
            }


    # ==========================================
    # AGENT 4 - RESPONSE AGENT
    # ==========================================

    def response_agent(
        self,
        severity,
        location
    ):

        if severity == "High":

            action = (
                f"Review the captured evidence immediately. "
                f"If confirmed, dispatch cleanup staff to "
                f"{location}."
            )

        elif severity == "Medium":

            action = (
                f"Review the incident evidence from "
                f"{location} and schedule cleanup "
                f"if waste remains."
            )

        else:

            action = (
                f"Continue monitoring {location}. "
                f"Escalate if similar activity "
                f"is detected again."
            )


        return {
            "agent": "Response Agent",
            "recommended_action": action
        }


    # ==========================================
    # ORCHESTRATOR
    # ==========================================

    def run(
        self,
        waste_type,
        location,
        confidence
    ):

        evidence = self.evidence_agent(
            waste_type,
            location,
            confidence
        )


        severity_result = self.severity_agent(
            confidence
        )


        investigation = self.investigation_agent(
            waste_type,
            location,
            confidence,
            severity_result["severity"]
        )


        response = self.response_agent(
            severity_result["severity"],
            location
        )


        return {

            "timestamp":
                datetime.now().isoformat(),

            "agents_executed": [
                evidence,
                severity_result,
                investigation,
                response
            ],

            "severity":
                severity_result["severity"],

            "summary":
                investigation["summary"],

            "recommended_action":
                response["recommended_action"],

            "ai_engine":
                investigation["source"]
        }