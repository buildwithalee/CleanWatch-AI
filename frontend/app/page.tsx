"use client";

import { useEffect, useState } from "react";
import LiveCamera from "./components/LiveCamera";

const API_URL = "https://overplay-saline-escargot.ngrok-free.dev";

type AgentTrace = {
  agent: string;
  result?: string;
  severity?: string;
  reason?: string;
  summary?: string;
  recommended_action?: string;
  source?: string;
};

type Incident = {
  id: string;
  waste_type: string;
  location: string;
  severity: string;
  status: string;
  confidence: number;
  timestamp: string;
  ai_summary: string;
  recommended_action: string;
  agent_trace?: AgentTrace[];
  ai_engine?: string;

  evidence_file?: string | null;
  detection_source?: string;
  event_type?: string;
};

export default function Home() {
  const [incidents, setIncidents] =
    useState<Incident[]>([]);

  const [selected, setSelected] =
    useState<Incident | null>(null);

  const [loading, setLoading] =
    useState(true);


  async function loadIncidents() {
    try {
      const response = await fetch(
  `${API_URL}/incidents`,
  {
    headers: {
      "ngrok-skip-browser-warning": "true",
    },
  }
);

      if (!response.ok) {
        throw new Error(
          "Failed to load incidents"
        );
      }

      const data = await response.json();

      setIncidents(data);
    } catch (error) {
      console.error(
        "Incident loading error:",
        error
      );
    } finally {
      setLoading(false);
    }
  }


  async function simulateIncident() {
    try {
      await fetch(
        `${API_URL}/incidents?waste_type=Plastic%20Bottle&location=Camera%2001%20-%20Demo%20Zone&confidence=91`,
        {
  method: "POST",
  headers: {
    "ngrok-skip-browser-warning": "true",
  },
}
      );

      await loadIncidents();
    } catch (error) {
      console.error(
        "Demo incident error:",
        error
      );
    }
  }


  async function resolveIncident(
    incidentId: string
  ) {
    try {
      await fetch(
        `${API_URL}/incidents/${incidentId}/resolve`,
       {
  method: "PATCH",
  headers: {
    "ngrok-skip-browser-warning": "true",
  },
}
      );

      setSelected(null);

      await loadIncidents();
    } catch (error) {
      console.error(
        "Resolve incident error:",
        error
      );
    }
  }


  useEffect(() => {
    loadIncidents();

    const interval = setInterval(
      loadIncidents,
      5000
    );

    return () =>
      clearInterval(interval);
  }, []);


  const total = incidents.length;

  const high = incidents.filter(
    (x) => x.severity === "High"
  ).length;

  const investigated = incidents.filter(
    (x) => x.status === "AI Investigated"
  ).length;

  const resolved = incidents.filter(
    (x) => x.status === "Resolved"
  ).length;


  return (
    <main className="min-h-screen bg-[#050810] text-white">

      {/* NAVBAR */}

      <nav className="border-b border-white/10 bg-[#080d18]">

        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">

          <div>

            <h1 className="text-xl font-bold">
              CleanWatch{" "}
              <span className="text-emerald-400">
                AI
              </span>
            </h1>

            <p className="text-xs text-gray-500">
              Agentic Waste Monitoring System
            </p>

          </div>


          <div className="flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-400">

            <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />

            AI System Online

          </div>

        </div>

      </nav>


      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* HERO */}

        <div className="mb-8 flex flex-col justify-between gap-5 md:flex-row md:items-center">

          <div>

            <p className="mb-2 text-xs font-semibold uppercase tracking-[0.3em] text-emerald-400">
              AI Command Center
            </p>

            <h2 className="text-3xl font-bold">
              Intelligent Waste Surveillance
            </h2>

            <p className="mt-2 max-w-2xl text-gray-400">
              Computer vision detects suspicious waste activity.
              AI agents investigate incidents, assess severity
              and recommend actions automatically.
            </p>

          </div>


          <button
            onClick={simulateIncident}
            className="rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-black transition hover:bg-emerald-300"
          >
            Run Demo Incident
          </button>

        </div>


        {/* STATS */}

        <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <Stat
            title="Total Incidents"
            value={total}
          />

          <Stat
            title="High Priority"
            value={high}
          />

          <Stat
            title="AI Investigated"
            value={investigated}
          />

          <Stat
            title="Resolved"
            value={resolved}
          />

        </div>


        {/* CAMERA + AGENTS */}

        <div className="mb-8 grid gap-6 lg:grid-cols-3">

          <section className="lg:col-span-2">
            <LiveCamera />
          </section>


          <section className="rounded-2xl border border-emerald-500/20 bg-[#0b111e] p-6">

            <p className="text-xs font-semibold uppercase tracking-widest text-emerald-400">
              Multi-Agent Pipeline
            </p>

            <h3 className="mt-2 text-xl font-semibold">
              Autonomous Investigation
            </h3>

            <p className="mt-2 text-xs text-gray-500">
              Vision evidence is processed through specialized
              agents before human review.
            </p>


            <div className="mt-6 space-y-5">

              <Pipeline
                number="01"
                title="Evidence Agent"
                text="Validates detected event evidence"
              />

              <Pipeline
                number="02"
                title="Severity Agent"
                text="Calculates initial incident priority"
              />

              <Pipeline
                number="03"
                title="Gemini Investigation Agent"
                text="Generates contextual AI assessment"
              />

              <Pipeline
                number="04"
                title="Response Agent"
                text="Recommends the next action"
              />

            </div>

          </section>

        </div>


        {/* INCIDENT TABLE */}

        <section className="rounded-2xl border border-white/10 bg-[#0b111e] p-6">

          <div className="mb-6 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">

            <div>

              <h3 className="text-xl font-semibold">
                Incident Intelligence
              </h3>

              <p className="text-sm text-gray-500">
                Real-time AI investigation results
              </p>

            </div>


            <div className="flex items-center gap-2 text-xs text-gray-500">

              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />

              Auto-refreshing

            </div>

          </div>


          {loading ? (

            <p className="text-gray-500">
              Loading incidents...
            </p>

          ) : incidents.length === 0 ? (

            <div className="py-12 text-center">

              <p className="text-gray-300">
                No incidents recorded.
              </p>

              <p className="mt-2 text-sm text-gray-600">
                Start live monitoring or run a demo incident.
              </p>

            </div>

          ) : (

            <div className="overflow-x-auto">

              <table className="w-full text-left">

                <thead>

                  <tr className="border-b border-white/10 text-xs uppercase text-gray-500">

                    <th className="pb-4">
                      Incident
                    </th>

                    <th className="pb-4">
                      Waste
                    </th>

                    <th className="pb-4">
                      Location
                    </th>

                    <th className="pb-4">
                      Severity
                    </th>

                    <th className="pb-4">
                      Confidence
                    </th>

                    <th className="pb-4">
                      Status
                    </th>

                    <th className="pb-4">
                      AI Engine
                    </th>

                    <th className="pb-4">
                      Action
                    </th>

                  </tr>

                </thead>


                <tbody>

                  {incidents.map(
                    (incident) => (

                      <tr
                        key={incident.id}
                        className="border-b border-white/5 text-sm"
                      >

                        <td className="py-5 font-mono text-emerald-400">
                          {incident.id}
                        </td>

                        <td>
                          {incident.waste_type}
                        </td>

                        <td className="text-gray-400">
                          {incident.location}
                        </td>

                        <td>
                          <Severity
                            value={
                              incident.severity
                            }
                          />
                        </td>

                        <td>
                          {incident.confidence}%
                        </td>

                        <td className="text-gray-400">
                          {incident.status}
                        </td>

                        <td>

                          {incident.ai_engine ===
                          "Google Gemini" ? (

                            <span className="rounded-md bg-blue-500/10 px-2 py-1 text-xs text-blue-400">
                              Gemini
                            </span>

                          ) : (

                            <span className="rounded-md bg-white/5 px-2 py-1 text-xs text-gray-500">
                              {incident.ai_engine ||
                                "Local"}
                            </span>

                          )}

                        </td>

                        <td>

                          <button
                            onClick={() =>
                              setSelected(
                                incident
                              )
                            }
                            className="rounded-lg border border-white/10 px-3 py-2 text-xs transition hover:bg-white/5"
                          >
                            Investigate
                          </button>

                        </td>

                      </tr>

                    )
                  )}

                </tbody>

              </table>

            </div>

          )}

        </section>


        <footer className="py-8 text-center text-xs text-gray-600">
          CleanWatch AI • Computer Vision + Gemini + Agentic Decision System
        </footer>

      </div>


      {/* INVESTIGATION MODAL */}

      {selected && (

        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-5">

          <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-2xl border border-white/10 bg-[#0b111e] p-7">


            {/* MODAL HEADER */}

            <div className="flex items-start justify-between">

              <div>

                <p className="font-mono text-sm text-emerald-400">
                  {selected.id}
                </p>

                <h2 className="mt-2 text-2xl font-bold">
                  AI Investigation
                </h2>


                <div className="mt-2 flex items-center gap-2">

                  <span className="text-xs text-gray-500">
                    AI Engine:
                  </span>

                  <span
                    className={`rounded-md px-2 py-1 text-xs ${
                      selected.ai_engine ===
                      "Google Gemini"
                        ? "bg-blue-500/10 text-blue-400"
                        : "bg-white/5 text-gray-400"
                    }`}
                  >
                    {selected.ai_engine ||
                      "Local Fallback"}
                  </span>

                </div>

              </div>


              <button
                onClick={() =>
                  setSelected(null)
                }
                className="text-xl text-gray-500 transition hover:text-white"
              >
                ✕
              </button>

            </div>


            {/* INCIDENT INFO */}

            <div className="mt-6 grid grid-cols-2 gap-4">

              <Info
                label="Waste"
                value={selected.waste_type}
              />

              <Info
                label="Location"
                value={selected.location}
              />

              <Info
                label="Severity"
                value={selected.severity}
              />

              <Info
                label="Confidence"
                value={`${selected.confidence}%`}
              />

            </div>


            {/* EVIDENCE */}

            {selected.evidence_file && (

              <div className="mt-6 rounded-xl border border-cyan-500/20 bg-black/20 p-4">

                <div className="mb-4 flex items-center justify-between">

                  <div>

                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-400">
                      Vision Evidence
                    </p>

                    <h3 className="mt-1 font-semibold text-white">
                      Captured Incident Frame
                    </h3>

                  </div>


                  <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs text-emerald-400">
                    YOLO Evidence
                  </span>

                </div>


                <div className="overflow-hidden rounded-xl border border-white/10 bg-black">

                  {/* eslint-disable-next-line @next/next/no-img-element */}

                  <img
                    src={`${API_URL}/evidence/${selected.evidence_file}`}
                    alt="CleanWatch incident evidence"
                    className="max-h-[430px] w-full object-contain"
                  />

                </div>


                <div className="mt-3 flex flex-col justify-between gap-2 text-xs text-gray-500 sm:flex-row">

                  <span>
                    {selected.location}
                  </span>

                  <span>
                    {selected.timestamp}
                  </span>

                </div>

              </div>

            )}


            {/* NO EVIDENCE FOR OLD/DEMO RECORD */}

            {!selected.evidence_file && (

              <div className="mt-6 rounded-xl border border-white/10 bg-black/20 p-4">

                <p className="text-xs uppercase tracking-wider text-gray-500">
                  Vision Evidence
                </p>

                <p className="mt-2 text-sm text-gray-400">
                  No captured frame is available for this incident.
                  Live YOLO-generated incidents will include evidence.
                </p>

              </div>

            )}


            {/* AI ASSESSMENT */}

            <div className="mt-6 rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-5">

              <div className="flex items-center justify-between">

                <p className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
                  AI Assessment
                </p>


                {selected.ai_engine ===
                  "Google Gemini" && (

                  <span className="rounded-md bg-blue-500/10 px-2 py-1 text-xs text-blue-400">
                    Powered by Gemini
                  </span>

                )}

              </div>


              <p className="mt-3 text-sm leading-6 text-gray-300">
                {selected.ai_summary}
              </p>

            </div>


            {/* RECOMMENDED ACTION */}

            <div className="mt-4 rounded-xl border border-white/10 p-5">

              <p className="text-xs uppercase text-gray-500">
                Recommended Action
              </p>

              <p className="mt-3 text-sm leading-6 text-gray-300">
                {selected.recommended_action}
              </p>

            </div>


            {/* AGENT TRACE */}

            {selected.agent_trace && (

              <div className="mt-6">

                <h3 className="mb-4 font-semibold">
                  Agent Execution Trace
                </h3>


                <div className="space-y-3">

                  {selected.agent_trace.map(
                    (agent, index) => (

                      <div
                        key={index}
                        className="rounded-xl border border-white/10 bg-black/20 p-4"
                      >

                        <div className="flex items-center justify-between">

                          <p className="text-sm font-semibold text-emerald-400">
                            {index + 1}.{" "}
                            {agent.agent}
                          </p>


                          {agent.source && (

                            <span className="text-xs text-gray-500">
                              {agent.source}
                            </span>

                          )}

                        </div>


                        <p className="mt-2 text-xs leading-5 text-gray-400">

                          {agent.result ||
                            agent.reason ||
                            agent.summary ||
                            agent.recommended_action}

                        </p>

                      </div>

                    )
                  )}

                </div>

              </div>

            )}


            {/* RESOLVE */}

            {selected.status !==
              "Resolved" && (

              <button
                onClick={() =>
                  resolveIncident(
                    selected.id
                  )
                }
                className="mt-7 w-full rounded-xl bg-emerald-400 py-3 font-semibold text-black transition hover:bg-emerald-300"
              >
                Mark Incident Resolved
              </button>

            )}

          </div>

        </div>

      )}

    </main>
  );
}


function Stat({
  title,
  value,
}: {
  title: string;
  value: number;
}) {
  return (

    <div className="rounded-2xl border border-white/10 bg-[#0b111e] p-5">

      <p className="text-sm text-gray-500">
        {title}
      </p>

      <p className="mt-2 text-3xl font-bold">
        {value}
      </p>

    </div>

  );
}


function Pipeline({
  number,
  title,
  text,
}: {
  number: string;
  title: string;
  text: string;
}) {
  return (

    <div className="flex gap-3">

      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-emerald-500/10 text-xs font-bold text-emerald-400">
        {number}
      </div>

      <div>

        <p className="text-sm font-medium">
          {title}
        </p>

        <p className="text-xs text-gray-500">
          {text}
        </p>

      </div>

    </div>

  );
}


function Severity({
  value,
}: {
  value: string;
}) {
  const style =
    value === "High"
      ? "bg-red-500/10 text-red-400"
      : value === "Medium"
      ? "bg-orange-500/10 text-orange-400"
      : "bg-green-500/10 text-green-400";

  return (

    <span
      className={`rounded-md px-2 py-1 text-xs ${style}`}
    >
      {value}
    </span>

  );
}


function Info({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (

    <div className="rounded-xl border border-white/10 p-4">

      <p className="text-xs text-gray-500">
        {label}
      </p>

      <p className="mt-1 text-sm font-medium">
        {value}
      </p>

    </div>

  );
}