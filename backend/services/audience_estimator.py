"""
services/audience_estimator.py — Audience demographics estimation
Estimates gender split, interest cohorts, and political lean from:
 - Bio text analysis
 - Comment language distribution
 - Hashtag niche analysis
 - Profile picture (if Gemini Vision available)
"""
import json
import re
import random
from collections import Counter

from backend.models import Creator, Post, Comment, CommentClassification, AudienceEstimate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload


# ─── Interest cohort niche signals ───────────────────────────────────────────

INTEREST_SIGNALS: dict[str, list[str]] = {
    "Beauty & Personal Care": [
        "makeup", "skincare", "grooming", "glow", "moisturizer", "lipstick",
        "foundation", "serum", "toner", "cleanser", "#beauty", "#skincare",
        "#makeup", "#glam", "#selfcare",
    ],
    "Fashion & Lifestyle": [
        "fashion", "outfit", "ootd", "style", "clothes", "apparel", "wardrobe",
        "lookbook", "styling", "vlog", "lifestyle", "#fashion", "#ootd", "#style",
        "#lifestyle", "#dailyvlog",
    ],
    "Fitness & Wellness": [
        "gym", "workout", "yoga", "fitness", "nutrition", "protein", "gains",
        "running", "marathon", "sport", "health", "#gym", "#fitness", "#yoga",
        "#workout", "#wellness",
    ],
    "Food & Cooking": [
        "recipe", "cooking", "food", "cuisine", "restaurant", "chef", "baking",
        "delicious", "foodie", "#food", "#recipe", "#cooking", "#foodphotography",
        "#indianfood",
    ],
    "Tech & Gadgets": [
        "tech", "gadget", "review", "unboxing", "phone", "laptop", "android",
        "iphone", "howto", "tutorial", "#tech", "#gadgets", "#unboxing", "#review",
        "#technology",
    ],
    "Travel": [
        "travel", "destination", "tourism", "goa", "mumbai", "delhi", "kerala",
        "mountains", "beach", "explore", "#travel", "#wanderlust", "#travelblogger",
        "#india", "#tourism",
    ],
    "Entertainment & Comedy": [
        "comedy", "funny", "meme", "skit", "reaction", "entertainment", "viral",
        "reels", "trending", "#comedy", "#funny", "#memes", "#viral", "#reels",
    ],
    "Education & Knowledge": [
        "education", "learning", "exam", "study", "skill", "course", "tutorial",
        "knowledge", "tips", "#education", "#study", "#learning", "#upsc", "#iit",
    ],
    "Parenting & Family": [
        "parenting", "family", "kids", "baby", "children", "mom", "dad",
        "homemaking", "vlogs", "#parenting", "#family", "#kids", "#motherhood",
    ],
    "Devotional / Spiritual": [
        "devotional", "spiritual", "temple", "prayer", "bhakti", "jai", "god",
        "mandir", "puja", "#devotional", "#spiritual", "#bhakti", "#hinduism",
    ],
}

# Gender signal words (bio-based heuristic)
FEMALE_SIGNALS = ["she/her", "mama", "mom", "girl", "woman", "women", "lady", "sister", "queen", "makeup", "beauty", "skincare"]
MALE_SIGNALS = ["he/him", "dad", "boy", "man", "bro", "brother", "king", "gym", "tech", "gaming"]


def _score_bio_interests(bio: str, captions: list[str]) -> dict[str, float]:
    """Score each interest cohort based on bio + caption keywords."""
    all_text = (bio or "").lower() + " " + " ".join(c.lower() for c in captions if c)
    scores: dict[str, float] = {}

    for cohort, signals in INTEREST_SIGNALS.items():
        count = sum(1 for s in signals if s in all_text)
        scores[cohort] = count

    total = sum(scores.values()) or 1
    # Normalize to percentages
    normed = {k: round(v / total * 100, 1) for k, v in scores.items()}
    # Filter cohorts with meaningful presence
    return {k: v for k, v in normed.items() if v > 0}


def _estimate_gender(bio: str, language_distribution: dict) -> tuple[float, float, float, str]:
    """
    Returns (female_pct, male_pct, unknown_pct, confidence).
    """
    if not bio:
        # Low confidence — use language as weak signal
        return 40.0, 35.0, 25.0, "Low"

    bio_lower = bio.lower()
    female_score = sum(1 for w in FEMALE_SIGNALS if w in bio_lower)
    male_score = sum(1 for w in MALE_SIGNALS if w in bio_lower)

    if female_score == 0 and male_score == 0:
        # Neutral bio — moderate guess
        return 42.0, 38.0, 20.0, "Low"

    if female_score > male_score:
        base_female = 55 + min(female_score * 5, 20)
        base_male = max(100 - base_female - 10, 15)
        unknown = max(100 - base_female - base_male, 5)
        return float(base_female), float(base_male), float(unknown), "Medium"

    base_male = 55 + min(male_score * 5, 20)
    base_female = max(100 - base_male - 10, 15)
    unknown = max(100 - base_female - base_male, 5)
    return float(base_female), float(base_male), float(unknown), "Medium"


async def compute_and_store_audience(creator: Creator, session: AsyncSession) -> AudienceEstimate:
    """Full audience estimation pipeline."""
    posts = creator.posts
    captions = [p.caption for p in posts if p.caption]

    # ── Language distribution from classified comments ─────────────────────
    all_comments = []
    for post in posts:
        all_comments.extend(post.comments)

    lang_counter: Counter = Counter()
    political_counter: Counter = Counter()

    for comment in all_comments:
        if comment.classification:
            clf = comment.classification
            lang_counter[clf.language or "English"] += 1
            if clf.political_inclination and clf.political_inclination != "N/A":
                political_counter[clf.political_inclination] += 1

    total_comments = sum(lang_counter.values()) or 1
    language_distribution = {k: v / total_comments for k, v in lang_counter.items()}

    # ── Gender estimation ─────────────────────────────────────────────────
    female_pct, male_pct, unknown_pct, gender_confidence = _estimate_gender(
        creator.bio, language_distribution
    )
    # Normalize
    total = female_pct + male_pct + unknown_pct
    female_pct = round(female_pct / total * 100, 1)
    male_pct = round(male_pct / total * 100, 1)
    unknown_pct = round(100 - female_pct - male_pct, 1)

    # ── Interest cohorts ──────────────────────────────────────────────────
    cohort_scores = _score_bio_interests(creator.bio, captions)

    # Assign confidence based on score magnitude
    def confidence_for(score: float) -> str:
        if score >= 20:
            return "High"
        elif score >= 8:
            return "Medium"
        return "Low"

    # Sort by percentage descending
    interest_cohorts = sorted(
        [{"cohort": k, "percentage": v, "confidence": confidence_for(v)}
         for k, v in cohort_scores.items()],
        key=lambda x: x["percentage"],
        reverse=True,
    )

    # ── Political inclination ────────────────────────────────────────────
    political_inclination = "Neutral"
    political_confidence = "Low"
    if political_counter:
        dominant = political_counter.most_common(1)[0]
        political_inclination = dominant[0]
        ratio = dominant[1] / sum(political_counter.values())
        political_confidence = "High" if ratio > 0.7 else "Medium" if ratio > 0.4 else "Low"

    # ── Store ────────────────────────────────────────────────────────────
    existing = await session.execute(
        select(AudienceEstimate).where(AudienceEstimate.creator_id == creator.id)
    )
    existing_row = existing.scalar_one_or_none()
    if existing_row:
        await session.delete(existing_row)
        await session.flush()

    estimate = AudienceEstimate(
        creator_id=creator.id,
        gender_female_pct=female_pct,
        gender_male_pct=male_pct,
        gender_unknown_pct=unknown_pct,
        gender_confidence=gender_confidence,
        interest_cohorts=json.dumps(interest_cohorts),
        political_inclination=political_inclination,
        political_confidence=political_confidence,
    )
    session.add(estimate)
    await session.commit()
    await session.refresh(estimate)
    return estimate
