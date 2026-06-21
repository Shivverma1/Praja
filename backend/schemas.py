"""
schemas.py — Pydantic v2 request/response schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# ─── Shared ───────────────────────────────────────────────────────────────────

class OrmBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ─── Comment Classification ───────────────────────────────────────────────────

class CommentClassificationOut(OrmBase):
    authenticity: Optional[str] = None
    bot_likelihood: Optional[str] = None
    political_inclination: Optional[str] = None
    relevance: Optional[str] = None
    comment_type: Optional[str] = None
    language: Optional[str] = None
    requires_manual_review: bool = False


class CommentOut(OrmBase):
    id: int
    text: str
    username: Optional[str] = None
    commented_at: Optional[datetime] = None
    classification: Optional[CommentClassificationOut] = None


# ─── Post ─────────────────────────────────────────────────────────────────────

class PostOut(OrmBase):
    id: int
    shortcode: Optional[str] = None
    post_type: str
    thumbnail_url: Optional[str] = None
    caption: Optional[str] = None
    hashtag_list: list[str] = []
    likes: int
    comments_count: int
    shares: int
    saves: int
    posted_at: Optional[datetime] = None
    is_collaboration: bool


# ─── Engagement Metrics ───────────────────────────────────────────────────────

class HashtagEntry(BaseModel):
    tag: str
    count: int


class CollabPostBrief(OrmBase):
    id: int
    shortcode: Optional[str] = None
    thumbnail_url: Optional[str] = None
    likes: int
    comments_count: int
    saves: int
    engagement_rate: Optional[float] = None


class EngagementMetricsOut(OrmBase):
    avg_likes: float
    avg_comments: float
    avg_shares: float
    avg_saves: float
    engagement_rate: float
    top_hashtag_list: list


# ─── Audience Estimate ────────────────────────────────────────────────────────

class InterestCohort(BaseModel):
    cohort: str
    percentage: float
    confidence: str   # High / Medium / Low


class AudienceEstimateOut(OrmBase):
    gender_female_pct: float
    gender_male_pct: float
    gender_unknown_pct: float
    gender_confidence: str
    interest_cohort_list: list
    political_inclination: Optional[str] = None
    political_confidence: str
    computed_at: Optional[datetime] = None


# ─── Creator ──────────────────────────────────────────────────────────────────

class CreatorOut(OrmBase):
    id: int
    handle: str
    display_name: Optional[str] = None
    profile_pic_url: Optional[str] = None
    bio: Optional[str] = None
    external_link: Optional[str] = None
    verified: bool
    follower_count: int
    following_count: int
    post_count: int
    fetched_at: Optional[datetime] = None
    pipeline_status: str
    pipeline_progress: int
    pipeline_message: Optional[str] = None


class CreatorDetailOut(CreatorOut):
    posts: list[PostOut] = []
    engagement_metrics: Optional[EngagementMetricsOut] = None
    audience_estimate: Optional[AudienceEstimateOut] = None


# ─── Classification Summary (aggregated) ─────────────────────────────────────

class ClassificationSummary(BaseModel):
    total_comments: int
    genuine_ratio: float   # 0.0–1.0

    authenticity_breakdown: dict[str, int]
    bot_likelihood_breakdown: dict[str, int]
    political_breakdown: dict[str, int]
    relevance_breakdown: dict[str, int]
    type_breakdown: dict[str, int]
    language_breakdown: dict[str, int]
    manual_review_count: int


# ─── Pipeline Status ──────────────────────────────────────────────────────────

class PipelineStatusOut(BaseModel):
    handle: str
    status: str         # pending | running | complete | error
    progress: int       # 0–100
    message: Optional[str] = None


# ─── Request ──────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    handle: str
    force_refresh: bool = False
