from datetime import datetime


class CleanWatchAgents:

    def evidence_agent(self, waste_type, location, confidence):
        return {
            "agent": "Evidence Agent",
            "result": (
                f"{waste_type} activity detected at {location} "
                f"with {confidence}% confidence."
            )
        }

    def severity_agent(self, waste_type, confidence):
        if confidence >= 90:
            severity = "High"
        elif confidence >= 70:
            severity = "Medium"
        else:
            severity = "Low"

        return {
            "agent": "Severity Agent",
            "severity": severity,
            "reason": (
                f"Severity classified as {severity} based on "
                f"detection confidence and waste activity."
            )
        }

    def investigation_agent(
        self,
        waste_type,
        location,
        confidence
    ):
        return {
            "agent": "Investigation Agent",
            "summary": (
                f"A possible illegal waste disposal event involving "
                f"{waste_type} was detected at {location}. "
                f"The visual detection confidence is {confidence}%."
            )
        }

    def response_agent(self, severity, location):
        if severity == "High":
            action = (
                f"Immediately inspect {location}, preserve the evidence, "
                f"and dispatch the cleanup team."
            )

        elif severity == "Medium":
            action = (
                f"Review the captured evidence from {location} and "
                f"send cleaning staff if the waste remains."
            )

        else:
            action = (
                f"Continue monitoring {location} and review the event "
                f"if similar activity occurs again."
            )

        return {
            "agent": "Response Agent",
            "recommended_action": action
        }

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
            waste_type,
            confidence
        )

        investigation = self.investigation_agent(
            waste_type,
            location,
            confidence
        )

        response = self.response_agent(
            severity_result["severity"],
            location
        )

        return {
            "timestamp": datetime.now().isoformat(),

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
                response["recommended_action"]
        }