# Offline SAT Academy

Offline SAT Academy is a local-first SAT practice platform for adaptive practice, AI tutoring, full Digital SAT simulation, weakness tracking, spaced repetition, and analytics. It is designed to run fully on a local machine using SQLite, IndexedDB, LM Studio, and an Ollama fallback.

## Stack

- Frontend: React + Vite + TypeScript
- Backend: FastAPI + SQLAlchemy + SQLite
- Charts: Recharts
- Local AI: LM Studio OpenAI-compatible API with Ollama fallback
- Offline cache: SQLite on the backend and IndexedDB in the browser
- Packaging: Docker Compose plus local dev scripts

## Local Quick Start

1. Start LM Studio and enable the local server at `http://localhost:1234`.
2. Load your preferred model in LM Studio. The app will prefer `Qwen3 35B A3B` for tutoring and reasoning.
3. Start the backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Start the frontend:

```bash
cd frontend
npm install
npm run dev
```

5. Open `http://localhost:5173`.

## Docker

```bash
docker compose up --build
```

The backend stores data in `backend/data/sat_academy.sqlite3`.

## Core Features

- Digital SAT-aligned curriculum map for Math and Reading/Writing
- Practice mode with adaptive question selection
- Full SAT simulation with timed modules, review flags, calculator mode, and break timer
- AI tutor with streaming local responses
- Mistake analysis and reinforcement question generation
- Leitner spaced repetition for flashcards and missed questions
- Score prediction with probability bands for 1200, 1300, 1400, 1500+, and 1550+
- Analytics dashboard with trends, radar charts, topic mastery, and time analysis
- Offline video recommendation metadata for persistent weaknesses
- Dark/light responsive interface

## AI Model Routing

The backend automatically routes tasks:

- Reasoning, tutoring, remediation: `Qwen3 35B A3B`
- Fast grading and instant feedback: `GPT-OSS 20B`, then `GLM 4.7 Flash`
- Fallback: `Gemma 4 31B`

If LM Studio is unavailable, the AI service tries Ollama at `http://localhost:11434`.

## Testing

```bash
cd backend
pytest

cd ../frontend
npm run test
```

## Offline Posture

The application does not require cloud services. YouTube recommendations are stored as local metadata and remain optional links. No telemetry is implemented.
