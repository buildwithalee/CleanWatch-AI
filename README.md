# CleanWatch AI

## Agentic Waste Monitoring System

CleanWatch AI is an intelligent waste surveillance system that combines Computer Vision, event detection, FastAPI, and a multi-agent decision pipeline to detect and investigate possible illegal waste dumping incidents.

## Problem

Traditional CCTV systems only record footage and require continuous human monitoring.

CleanWatch AI converts passive cameras into an intelligent monitoring system capable of detecting suspicious waste activity and automatically creating actionable incidents.

## Solution

The system monitors a camera feed using YOLO and detects people and waste-related objects.

When suspicious dumping behavior is detected, evidence is captured and sent to the CleanWatch backend.

A multi-agent pipeline then investigates the incident and generates an assessment and recommended response.

## System Flow

Camera / Video
→ YOLO Detection
→ Dumping Event Detection
→ Evidence Capture
→ FastAPI Backend
→ Multi-Agent Investigation
→ Incident Dashboard
→ Human Review & Resolution

## Multi-Agent Architecture

### 1. Evidence Agent
Validates and summarizes detection evidence.

### 2. Severity Agent
Assigns incident priority based on detection information.

### 3. Investigation Agent
Analyzes the incident context and generates an assessment.

### 4. Response Agent
Recommends the appropriate response.

## Features

- Real-time webcam monitoring
- Person detection
- Waste-object detection
- Temporal dumping-event detection
- Automatic evidence capture
- Automatic incident creation
- Multi-agent investigation pipeline
- Severity classification
- Recommended actions
- Incident dashboard
- Agent execution trace
- Incident resolution workflow
- Automatic dashboard updates

## Technology Stack

### AI / Computer Vision
- Python
- YOLO11
- Ultralytics
- OpenCV

### Backend
- FastAPI
- Python

### Frontend
- Next.js
- TypeScript
- Tailwind CSS

### Architecture
- Computer Vision
- Event-driven processing
- Multi-agent decision workflow

## Run Backend

```bash
cd backend
uvicorn main:app --reload