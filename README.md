# multi modal 
    
## Overview
OncoDetect X is an AI-assisted cancer triage and decision-support system. It combines deep learning, deterministic risk logic, LLM-based cognitive reasoning, and **Gemini-powered multi-modal oncology analysis** to provide a comprehensive, multi-layered risk assessment for oncology cases.

## Features
- **Multi-Organ Support**: Brain, Lung, Breast
- **Perception Layer**: Simulates CNN analysis for initial confidence
- **Risk Aggregation**: Combines ML scores, symptoms, and risk factors deterministically
- **Cognitive Layer**: Uses LLM to contextualize findings and generate explanations
- **AI Oncologist Analysis**: Upload medical scans or enter symptoms for Gemini-powered cancer assessment with interactive charts
- **Hospital Recommendation**: Suggests nearby facilities based on specialization
- **Production-Grade UI**: Modern Next.js interface with interactive Plotly visualizations

## Tech Stack
- **Backend**: Python FastAPI
- **Frontend**: Next.js (React + TypeScript)
- **AI/LLM**: Google Gemini 1.5 Flash integration
- **Charts**: Plotly.js (react-plotly.js)

## Project Structure
```
Onco-Detect/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes.py          # Core triage endpoints
│   │   │   └── routes/
│   │   │       └── analysis.py    # Gemini AI analysis endpoint
│   │   ├── models/
│   │   │   └── schemas.py         # Pydantic models
│   │   └── services/
│   │       ├── cognitive.py       # LLM reasoning service
│   │       ├── gemini_service.py  # Gemini AI oncology service
│   │       ├── hospital.py        # Hospital recommendation
│   │       ├── perception.py      # ML perception layer
│   │       └── risk.py            # Risk calculation
│   ├── data/
│   │   └── hospitals.json
│   ├── logs/                      # Runtime logs
│   ├── tests/
│   │   └── test_api_integration.py
│   ├── main.py                    # FastAPI entry point
│   └── requirements.txt
├── frontend/
│   ├── src/app/
│   │   ├── analysis/
│   │   │   └── page.tsx           # AI Analysis page
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx               # Home page
│   └── package.json
├── start_backend.sh
├── start_frontend.sh
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- Gemini API Key (Set in `backend/.env` as `gemini_API_KEY`)

### Installation

1. **Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm install
   ```

### Running
- **Backend**: `./start_backend.sh` or `cd backend && uvicorn main:app --reload`
- **Frontend**: `./start_frontend.sh` or `cd frontend && npm run dev`
- Open `http://localhost:3000` in your browser
- Navigate to **AI Analysis** to use the Gemini-powered scanner

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/analyze` | Core triage analysis |
| POST | `/api/v1/ai-analyze` | Gemini AI oncology analysis |

## Disclaimer
This system is for **research and educational purposes only**. It does NOT diagnose cancer. All outputs should be verified by a medical professional.
