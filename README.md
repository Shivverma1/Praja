# Praja — Creator Intelligence Module

A production-grade full-stack application for Instagram creator analytics.

## Architecture

```
Praja/
├── backend/        FastAPI + SQLAlchemy + Gemini AI
└── frontend/       React 18 + Vite + Recharts
```

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Copy env file
cp .env.example .env

# (Optional) Add your API keys to .env
# APP_MODE=demo works without any keys

pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Backend runs at: http://localhost:8000  
API docs at: http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:5173

## API Keys (Optional)

| Key | Where to get | Used for |
|-----|-------------|---------|
| `GEMINI_API_KEY` | https://ai.google.dev/ | Comment AI classification |
| `INSTAGRAM_ACCESS_TOKEN` | Facebook Developers | Real Instagram data |
| `RAPIDAPI_KEY` | https://rapidapi.com | Instagram scraping fallback |

> Without keys: `APP_MODE=demo` uses realistic generated data with pre-classified comments.

## Features

- ✅ Profile: handle, bio, follower/following/post counts, verified status, ER
- ✅ 12 recent posts: likes, comments, shares, saves per post
- ✅ Collab detection via `#ad`, `#sponsored`, `#collab` etc.
- ✅ Comment classification (6 dimensions via Gemini AI)
  - Authenticity, Bot-likelihood, Political inclination
  - Relevance, Comment type, Language/script
- ✅ Audience estimation: gender split, interest cohorts (10 niches), political lean
- ✅ Engagement rate: `(avg_likes + avg_comments + avg_saves) / followers × 100`
- ✅ Top hashtag cloud
- ✅ Real-time pipeline progress with background task

## Engagement Rate Formula

```
ER = (avg_likes + avg_comments + avg_saves) / follower_count × 100
```

**Justification**: Industry standard for Instagram. Saves are included (not shares) as Instagram rarely exposes shares and saves indicate high-intent engagement. Reported as a percentage.

## Comment Classification Dimensions

| Dimension | Values |
|---|---|
| Authenticity | Genuine / Spam |
| Bot-likelihood | Human / Likely-bot / Uncertain |
| Political Inclination | Positive / Neutral / Negative / N/A |
| Relevance | On-topic / Off-topic |
| Type | Praise / Question / Criticism / Tag-a-friend / Sales-or-promo / Other |
| Language | English / Hindi / Hinglish / Regional / Ambiguous |

Hinglish comments flagged as ambiguous are marked `requires_manual_review = true`.
