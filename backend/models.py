"""
models.py — SQLAlchemy ORM models for the Praja Creator Intelligence Module
"""
import json
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


# ─── Creator ──────────────────────────────────────────────────────────────────

class Creator(Base):
    __tablename__ = "creators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    handle: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(200))
    profile_pic_url: Mapped[Optional[str]] = mapped_column(Text)
    bio: Mapped[Optional[str]] = mapped_column(Text)
    external_link: Mapped[Optional[str]] = mapped_column(Text)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    follower_count: Mapped[int] = mapped_column(Integer, default=0)
    following_count: Mapped[int] = mapped_column(Integer, default=0)
    post_count: Mapped[int] = mapped_column(Integer, default=0)
    fetched_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())
    pipeline_status: Mapped[str] = mapped_column(String(50), default="pending")
    pipeline_progress: Mapped[int] = mapped_column(Integer, default=0)
    pipeline_message: Mapped[Optional[str]] = mapped_column(Text)

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="creator", cascade="all, delete-orphan")
    engagement_metrics: Mapped[Optional["EngagementMetrics"]] = relationship(
        "EngagementMetrics", back_populates="creator", uselist=False, cascade="all, delete-orphan"
    )
    audience_estimate: Mapped[Optional["AudienceEstimate"]] = relationship(
        "AudienceEstimate", back_populates="creator", uselist=False, cascade="all, delete-orphan"
    )


# ─── Post ─────────────────────────────────────────────────────────────────────

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("creators.id"), nullable=False)
    shortcode: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    post_type: Mapped[str] = mapped_column(String(20), default="personal")   # "personal" | "collab"
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text)
    caption: Mapped[Optional[str]] = mapped_column(Text)
    hashtags: Mapped[Optional[str]] = mapped_column(Text)          # JSON list
    likes: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    saves: Mapped[int] = mapped_column(Integer, default=0)
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_collaboration: Mapped[bool] = mapped_column(Boolean, default=False)

    creator: Mapped["Creator"] = relationship("Creator", back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )

    @property
    def hashtag_list(self) -> list:
        if self.hashtags:
            try:
                return json.loads(self.hashtags)
            except Exception:
                return []
        return []


# ─── Comment ──────────────────────────────────────────────────────────────────

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(100))
    commented_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    post: Mapped["Post"] = relationship("Post", back_populates="comments")
    classification: Mapped[Optional["CommentClassification"]] = relationship(
        "CommentClassification", back_populates="comment", uselist=False, cascade="all, delete-orphan"
    )


# ─── CommentClassification ────────────────────────────────────────────────────

class CommentClassification(Base):
    __tablename__ = "comment_classifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"), unique=True, nullable=False)

    # Authenticity: "Genuine" | "Spam"
    authenticity: Mapped[Optional[str]] = mapped_column(String(20))
    # Bot-likelihood: "Human" | "Likely-bot" | "Uncertain"
    bot_likelihood: Mapped[Optional[str]] = mapped_column(String(20))
    # Political: "Positive" | "Neutral" | "Negative" | "N/A"
    political_inclination: Mapped[Optional[str]] = mapped_column(String(20))
    # Relevance: "On-topic" | "Off-topic"
    relevance: Mapped[Optional[str]] = mapped_column(String(20))
    # Type: "Praise" | "Question" | "Criticism" | "Tag-a-friend" | "Sales-or-promo" | "Other"
    comment_type: Mapped[Optional[str]] = mapped_column(String(30))
    # Language: "English" | "Hindi" | "Hinglish" | "Regional" | "Ambiguous"
    language: Mapped[Optional[str]] = mapped_column(String(20))
    # Flag ambiguous Hinglish for manual review
    requires_manual_review: Mapped[bool] = mapped_column(Boolean, default=False)

    comment: Mapped["Comment"] = relationship("Comment", back_populates="classification")


# ─── EngagementMetrics ────────────────────────────────────────────────────────

class EngagementMetrics(Base):
    __tablename__ = "engagement_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("creators.id"), unique=True, nullable=False)

    avg_likes: Mapped[float] = mapped_column(Float, default=0.0)
    avg_comments: Mapped[float] = mapped_column(Float, default=0.0)
    avg_shares: Mapped[float] = mapped_column(Float, default=0.0)
    avg_saves: Mapped[float] = mapped_column(Float, default=0.0)
    # (avg_likes + avg_comments + avg_saves) / follower_count * 100
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)
    top_hashtags: Mapped[Optional[str]] = mapped_column(Text)   # JSON list of {tag, count}
    collab_post_id: Mapped[Optional[int]] = mapped_column(ForeignKey("posts.id"), nullable=True)

    creator: Mapped["Creator"] = relationship("Creator", back_populates="engagement_metrics")
    collab_post: Mapped[Optional["Post"]] = relationship("Post", foreign_keys=[collab_post_id])

    @property
    def top_hashtag_list(self) -> list:
        if self.top_hashtags:
            try:
                return json.loads(self.top_hashtags)
            except Exception:
                return []
        return []


# ─── AudienceEstimate ─────────────────────────────────────────────────────────

class AudienceEstimate(Base):
    __tablename__ = "audience_estimates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("creators.id"), unique=True, nullable=False)

    gender_female_pct: Mapped[float] = mapped_column(Float, default=0.0)
    gender_male_pct: Mapped[float] = mapped_column(Float, default=0.0)
    gender_unknown_pct: Mapped[float] = mapped_column(Float, default=0.0)
    gender_confidence: Mapped[str] = mapped_column(String(10), default="Low")   # High/Medium/Low

    # JSON: [{cohort, percentage, confidence}]
    interest_cohorts: Mapped[Optional[str]] = mapped_column(Text)

    political_inclination: Mapped[Optional[str]] = mapped_column(String(20))
    political_confidence: Mapped[str] = mapped_column(String(10), default="Low")

    computed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())

    creator: Mapped["Creator"] = relationship("Creator", back_populates="audience_estimate")

    @property
    def interest_cohort_list(self) -> list:
        if self.interest_cohorts:
            try:
                return json.loads(self.interest_cohorts)
            except Exception:
                return []
        return []
