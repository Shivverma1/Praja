# Praja — Creator Intelligence Module

A production-grade full-stack application for Instagram creator analytics.

## Architecture

```
Praja/
├── backend/        FastAPI + SQLAlchemy + Rule-based AI Classifier
└── frontend/       React 18 + Vite + Recharts
```

## Launch Video

Open [launch-video.html](launch-video.html) in your browser for a cinematic walkthrough of the product.

## Quick Start

### 1. Backend Setup

```bash
# From project root
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload
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

## App Modes

Set `APP_MODE` in `backend/.env`:

| Mode | Description |
|------|-------------|
| `demo` | Realistic mock data, no API keys needed (default) |
| `live` | Real Instagram data via Meta API + RapidAPI |

## API Keys (for live mode only)

| Key | Where to get | Used for |
|-----|-------------|---------|
| `INSTAGRAM_ACCESS_TOKEN` | Facebook Developers | Real Instagram data |
| `RAPIDAPI_KEY` | https://rapidapi.com | Instagram scraping fallback |

## Features

- ✅ Profile: handle, bio, follower/following/post counts, verified status, ER
- ✅ 12 recent posts: likes, comments, shares, saves per post (posts + reels)
- ✅ Collab detection via `#ad`, `#sponsored`, `#collab` etc.
- ✅ Comment classification (6 dimensions — fully offline, no AI API needed)
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

Classification uses VADER sentiment analysis + rule-based patterns — runs fully offline with no external AI API.
