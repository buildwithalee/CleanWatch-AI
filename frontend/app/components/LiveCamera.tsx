"use client";

import { useEffect, useRef, useState } from "react";

type Detection = {
  class: string;
  confidence: number;
};

type DetectionResponse = {
  success: boolean;
  status?: string;
  person_detected?: boolean;
  waste_detected?: boolean;
  waste_type?: string | null;
  confidence?: number;
  detections?: Detection[];
  error?: string;
};

export default function LiveCamera() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const requestRunningRef = useRef(false);

  const [isMonitoring, setIsMonitoring] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState("");

  const [visionStatus, setVisionStatus] = useState("WAITING");
  const [personDetected, setPersonDetected] = useState(false);
  const [wasteDetected, setWasteDetected] = useState(false);
  const [wasteType, setWasteType] = useState<string | null>(null);
  const [confidence, setConfidence] = useState(0);
  const [detections, setDetections] = useState<Detection[]>([]);

  async function analyzeFrame() {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) {
      return;
    }

    if (video.readyState < 2) {
      return;
    }

    if (requestRunningRef.current) {
      return;
    }

    const width = video.videoWidth;
    const height = video.videoHeight;

    if (!width || !height) {
      return;
    }

    const context = canvas.getContext("2d");

    if (!context) {
      return;
    }

    requestRunningRef.current = true;
    setIsAnalyzing(true);

    try {
      canvas.width = width;
      canvas.height = height;

      context.drawImage(
        video,
        0,
        0,
        width,
        height
      );

      const blob = await new Promise<Blob | null>(
        (resolve) => {
          canvas.toBlob(
            resolve,
            "image/jpeg",
            0.75
          );
        }
      );

      if (!blob) {
        return;
      }

      const formData = new FormData();

      formData.append(
        "file",
        blob,
        "camera-frame.jpg"
      );

      const response = await fetch(
        "https://overplay-saline-escargot.ngrok-free.dev/detect-frame",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(
          `Detection API error: ${response.status}`
        );
      }

      const data: DetectionResponse =
        await response.json();

      if (!data.success) {
        throw new Error(
          data.error || "YOLO detection failed"
        );
      }

      setVisionStatus(
        data.status || "CLEAR"
      );

      setPersonDetected(
        Boolean(data.person_detected)
      );

      setWasteDetected(
        Boolean(data.waste_detected)
      );

      setWasteType(
        data.waste_type || null
      );

      setConfidence(
        data.confidence || 0
      );

      setDetections(
        data.detections || []
      );

      setError("");
    } catch (err) {
      console.error(
        "Frame analysis error:",
        err
      );

      setError(
        "YOLO backend connection failed. Make sure FastAPI is running."
      );
    } finally {
      requestRunningRef.current = false;
      setIsAnalyzing(false);
    }
  }

  async function startCamera() {
    try {
      setError("");

      const stream =
        await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: "environment",
          },
          audio: false,
        });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;

        await videoRef.current.play();
      }

      setIsMonitoring(true);

      setVisionStatus("STARTING");

      setTimeout(() => {
        analyzeFrame();

        intervalRef.current = setInterval(
          analyzeFrame,
          1500
        );
      }, 1000);
    } catch (err) {
      console.error(
        "Camera error:",
        err
      );

      setError(
        "Camera access failed. Please allow camera permission in your browser."
      );
    }
  }

  function stopCamera() {
    if (intervalRef.current) {
      clearInterval(
        intervalRef.current
      );

      intervalRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current
        .getTracks()
        .forEach((track) => {
          track.stop();
        });

      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    requestRunningRef.current = false;

    setIsMonitoring(false);
    setIsAnalyzing(false);

    setVisionStatus("WAITING");

    setPersonDetected(false);
    setWasteDetected(false);

    setWasteType(null);
    setConfidence(0);
    setDetections([]);
  }

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(
          intervalRef.current
        );
      }

      if (streamRef.current) {
        streamRef.current
          .getTracks()
          .forEach((track) => {
            track.stop();
          });
      }
    };
  }, []);

  function getStatusText() {
    if (visionStatus === "PERSON_WITH_WASTE") {
      return "PERSON + WASTE DETECTED";
    }

    if (visionStatus === "WASTE_DETECTED") {
      return "WASTE DETECTED";
    }

    if (visionStatus === "PERSON_DETECTED") {
      return "PERSON DETECTED";
    }

    if (visionStatus === "CLEAR") {
      return "AREA CLEAR";
    }

    if (visionStatus === "STARTING") {
      return "STARTING AI VISION...";
    }

    return "WAITING";
  }

  function getStatusStyle() {
    if (visionStatus === "PERSON_WITH_WASTE") {
      return "border-red-500/30 bg-red-500/10 text-red-400";
    }

    if (visionStatus === "WASTE_DETECTED") {
      return "border-orange-500/30 bg-orange-500/10 text-orange-400";
    }

    if (visionStatus === "PERSON_DETECTED") {
      return "border-cyan-500/30 bg-cyan-500/10 text-cyan-400";
    }

    return "border-emerald-500/20 bg-emerald-500/10 text-emerald-400";
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-5">

      {/* HEADER */}

      <div className="mb-4 flex items-center justify-between">

        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">
            Live Vision
          </p>

          <h2 className="mt-1 text-xl font-semibold text-white">
            Camera Monitoring
          </h2>
        </div>

        <div
          className={`rounded-full px-3 py-1 text-xs font-medium ${
            isMonitoring
              ? "bg-green-500/15 text-green-400"
              : "bg-slate-700 text-slate-300"
          }`}
        >
          {isMonitoring
            ? "● MONITORING"
            : "OFFLINE"}
        </div>

      </div>


      {/* CAMERA */}

      <div className="relative aspect-video overflow-hidden rounded-xl bg-black">

        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="h-full w-full object-cover"
        />

        <canvas
          ref={canvasRef}
          className="hidden"
        />

        {!isMonitoring && (
          <div className="absolute inset-0 flex items-center justify-center">

            <div className="text-center">

              <div className="mb-2 text-4xl">
                📷
              </div>

              <p className="text-sm text-slate-400">
                Camera monitoring is offline
              </p>

            </div>

          </div>
        )}


        {isMonitoring && (
          <>
            <div className="absolute left-4 top-4 rounded-md bg-black/70 px-3 py-1 text-xs text-green-400">
              ● LIVE
            </div>

            <div className="absolute right-4 top-4 rounded-md bg-black/70 px-3 py-1 text-xs text-cyan-400">
              {isAnalyzing
                ? "YOLO ANALYZING..."
                : "YOLO ACTIVE"}
            </div>

            <div className="absolute bottom-4 left-4 rounded-md bg-black/70 px-3 py-1 text-xs text-white/80">
              Camera 01 • Demo Zone
            </div>
          </>
        )}

      </div>


      {/* YOLO STATUS */}

      {isMonitoring && (
        <div className="mt-4 grid gap-3 sm:grid-cols-3">

          <div
            className={`rounded-xl border p-3 ${getStatusStyle()}`}
          >
            <p className="text-[10px] uppercase tracking-wider opacity-70">
              Vision Status
            </p>

            <p className="mt-1 text-sm font-semibold">
              {getStatusText()}
            </p>
          </div>


          <div className="rounded-xl border border-white/10 bg-white/5 p-3">

            <p className="text-[10px] uppercase tracking-wider text-slate-500">
              Person
            </p>

            <p
              className={`mt-1 text-sm font-semibold ${
                personDetected
                  ? "text-cyan-400"
                  : "text-slate-400"
              }`}
            >
              {personDetected
                ? "DETECTED"
                : "NOT DETECTED"}
            </p>

          </div>


          <div className="rounded-xl border border-white/10 bg-white/5 p-3">

            <p className="text-[10px] uppercase tracking-wider text-slate-500">
              Waste
            </p>

            <p
              className={`mt-1 text-sm font-semibold ${
                wasteDetected
                  ? "text-orange-400"
                  : "text-slate-400"
              }`}
            >
              {wasteDetected
                ? `${wasteType || "Object"} ${confidence}%`
                : "NOT DETECTED"}
            </p>

          </div>

        </div>
      )}


      {/* DETECTION LIST */}

      {isMonitoring &&
        detections.length > 0 && (
          <div className="mt-3 rounded-xl border border-white/10 bg-black/20 p-3">

            <p className="mb-2 text-[10px] uppercase tracking-wider text-slate-500">
              YOLO Detections
            </p>

            <div className="flex flex-wrap gap-2">

              {detections.map(
                (detection, index) => (
                  <span
                    key={`${detection.class}-${index}`}
                    className="rounded-md border border-white/10 bg-white/5 px-2 py-1 text-xs text-slate-300"
                  >
                    {detection.class}{" "}
                    {detection.confidence}%
                  </span>
                )
              )}

            </div>

          </div>
        )}


      {/* ERROR */}

      {error && (
        <div className="mt-3 rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-400">
          {error}
        </div>
      )}


      {/* CONTROLS */}

      <div className="mt-4 flex gap-3">

        {!isMonitoring ? (
          <button
            onClick={startCamera}
            className="rounded-lg bg-cyan-500 px-5 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400"
          >
            Start Live Monitoring
          </button>
        ) : (
          <button
            onClick={stopCamera}
            className="rounded-lg bg-red-500 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-red-400"
          >
            Stop Monitoring
          </button>
        )}

      </div>

    </div>
  );
}