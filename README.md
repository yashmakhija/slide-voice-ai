# AI Voice Presentation

A voice-controlled slide presentation app powered by OpenAI's Realtime API. Users can navigate slides, ask questions, and interact with an AI assistant using natural speech.

**Live Demo:** https://slide-voice.iyash.me

## Features

- Voice-controlled slide navigation ("next slide", "go to slide 3")
- AI responses to questions about slide content
- Real-time user interruption handling
- Automatic slide switching based on conversation context
- Low-latency voice interaction

## Architecture

![Architecture Diagram](https://i.ibb.co/v6GkFyTk/Screenshot-2026-01-30-at-10-56-15-AM.png)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite, TypeScript, Zustand, Tailwind CSS, Framer Motion |
| Backend | FastAPI, Python 3.11, WebSocket, Pydantic |
| AI | OpenAI Realtime API (GPT-4o) |
| Infrastructure | Docker, GitHub Actions, Nginx, Certbot SSL |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Environment configuration
│   │   ├── models/              # Pydantic models
│   │   ├── routers/
│   │   │   └── websocket.py     # WebSocket endpoint
│   │   ├── services/
│   │   │   ├── realtime_client.py   # OpenAI Realtime API client
│   │   │   └── session_manager.py   # Voice session management
│   │   └── data/
│   │       └── slides.py        # Slide content
│   ├── tests/                   # 121 unit tests
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── SlideView.tsx
│   │   │   ├── SlideControls.tsx
│   │   │   └── VoiceIndicator.tsx
│   │   ├── contexts/
│   │   │   └── VoiceSessionContext.tsx  # WebSocket & audio handling
│   │   ├── stores/
│   │   │   └── presentation.ts  # Zustand state management
│   │   └── types/
│   └── package.json
│
└── .github/
    └── workflows/
        └── deploy.yml           # CI/CD pipeline
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- OpenAI API key with Realtime API access

### Backend Setup

```bash
cd backend

# Create environment file
echo "OPENAI_API_KEY=your-api-key-here" > .env

# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file (optional, for production API URL)
echo "VITE_API_URL=http://localhost:8000" > .env

# Run development server
npm run dev
```

Open http://localhost:5173 in your browser.

## Running Tests

```bash
cd backend

# Install dev dependencies
uv sync --all-extras

# Run tests
uv run pytest tests/ -v
```

**Test Coverage:** 121 tests covering:
- API endpoints
- WebSocket communication
- Session management
- Pydantic models
- Edge cases and error handling

## Docker

### Build

```bash
cd backend
docker build -t slide-voice-ai .
```

### Run

```bash
docker run -d \
  --name slide-voice-ai \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-api-key-here \
  slide-voice-ai
```

Or with env file:

```bash
docker run -d \
  --name slide-voice-ai \
  -p 8000:8000 \
  --env-file .env \
  slide-voice-ai
```

## Deployment

### CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/deploy.yml`) automatically:

1. Runs tests on every push to `main`
2. Builds Docker image
3. Pushes to Docker Hub
4. Deploys to VPS via SSH

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `VPS_HOST` | VPS IP address |
| `VPS_USER` | SSH username (e.g., `root`) |
| `VPS_SSH_KEY` | Private SSH key for VPS access |

### Nginx Configuration (Production)

```nginx
server {
    listen 443 ssl;
    server_name slide-api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/slide-api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/slide-api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## API Endpoints

### REST

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/slides` | Get all slides |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `/ws` | Voice session connection |

#### Client → Server Messages

```json
{ "type": "session.start" }
{ "type": "session.stop" }
{ "type": "audio.input", "audio": "<base64>" }
```

#### Server → Client Messages

```json
{ "type": "session.started", "session_id": "..." }
{ "type": "session.stopped" }
{ "type": "audio.output", "audio": "<base64>" }
{ "type": "audio.done" }
{ "type": "audio.interrupted" }
{ "type": "slide.changed", "slide_id": 3 }
{ "type": "transcript", "speaker": "user|assistant", "text": "..." }
{ "type": "error", "message": "..." }
```

## Voice Commands

| Command | Action |
|---------|--------|
| "Next slide" | Go to next slide |
| "Previous slide" | Go to previous slide |
| "Go to slide 3" | Navigate to specific slide |
| "What is this about?" | AI explains current slide |
| Any question | AI responds with context |

## Environment Variables

### Backend

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key |

### Frontend

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | No | Backend API URL (default: same origin) |

## License

MIT
