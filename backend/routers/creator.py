"""
routers/creator.py — Creator profile endpoints
"""
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.database import get_db
from backend.models import Creator, Post, Comment
from backend.schemas import (
    AnalyzeRequest, CreatorDetailOut, CreatorOut, PipelineStatusOut,
    ClassificationSummary,
)
from backend.pipeline import run_pipeline

router = APIRouter(prefix="/api/creator", tags=["creator"])


@router.post("/analyze")
async def analyze_creator(
    body: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Trigger full analysis pipeline for a creator handle."""
    handle = body.handle.lower().strip().lstrip("@")

    # Check if already running or complete
    result = await db.execute(select(Creator).where(Creator.handle == handle))
    creator = result.scalar_one_or_none()

    if creator and creator.pipeline_status == "running" and not body.force_refresh:
        return {"message": "Pipeline already running", "handle": handle, "status": "running"}

    if creator and creator.pipeline_status == "complete" and not body.force_refresh:
        return {"message": "Analysis already complete. Use force_refresh=true to rerun.", "handle": handle, "status": "complete"}

    # Reset or create
    try:
        if not creator:
            creator = Creator(handle=handle, pipeline_status="pending", pipeline_progress=0)
            db.add(creator)
            await db.commit()
        else:
            creator.pipeline_status = "pending"
            creator.pipeline_progress = 0
            creator.pipeline_message = None
            await db.commit()
    except Exception:
        await db.rollback()
        return {"message": "Pipeline already running", "handle": handle, "status": "running"}

    background_tasks.add_task(run_pipeline, handle)
    return {"message": "Pipeline started", "handle": handle, "status": "pending"}


@router.get("/{handle}/status", response_model=PipelineStatusOut)
async def get_pipeline_status(handle: str, db: AsyncSession = Depends(get_db)):
    """Poll pipeline progress."""
    handle = handle.lower().strip().lstrip("@")
    result = await db.execute(select(Creator).where(Creator.handle == handle))
    creator = result.scalar_one_or_none()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found. Start analysis first.")
    return PipelineStatusOut(
        handle=handle,
        status=creator.pipeline_status,
        progress=creator.pipeline_progress,
        message=creator.pipeline_message,
    )


@router.get("/{handle}", response_model=CreatorDetailOut)
async def get_creator(handle: str, db: AsyncSession = Depends(get_db)):
    """Get full creator profile with posts, metrics, and audience."""
    handle = handle.lower().strip().lstrip("@")
    result = await db.execute(
        select(Creator)
        .where(Creator.handle == handle)
        .options(
            selectinload(Creator.posts),
            selectinload(Creator.engagement_metrics),
            selectinload(Creator.audience_estimate),
        )
    )
    creator = result.scalar_one_or_none()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found.")
    return CreatorDetailOut.model_validate(creator)


@router.get("/{handle}/classification-summary", response_model=ClassificationSummary)
async def get_classification_summary(handle: str, db: AsyncSession = Depends(get_db)):
    """Aggregate comment classification breakdown for all posts."""
    handle = handle.lower().strip().lstrip("@")
    result = await db.execute(
        select(Creator)
        .where(Creator.handle == handle)
        .options(
            selectinload(Creator.posts)
            .selectinload(Post.comments)
            .selectinload(Comment.classification)
        )
    )
    creator = result.scalar_one_or_none()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found.")

    all_classifs = []
    for post in creator.posts:
        for comment in post.comments:
            if comment.classification:
                all_classifs.append(comment.classification)

    total = len(all_classifs)
    if total == 0:
        return ClassificationSummary(
            total_comments=0, genuine_ratio=0.0,
            authenticity_breakdown={}, bot_likelihood_breakdown={},
            political_breakdown={}, relevance_breakdown={},
            type_breakdown={}, language_breakdown={}, manual_review_count=0,
        )

    def breakdown(attr: str) -> dict:
        counter: dict = {}
        for c in all_classifs:
            val = getattr(c, attr) or "Unknown"
            counter[val] = counter.get(val, 0) + 1
        return counter

    genuine_count = sum(1 for c in all_classifs if c.authenticity == "Genuine")
    manual_count = sum(1 for c in all_classifs if c.requires_manual_review)

    return ClassificationSummary(
        total_comments=total,
        genuine_ratio=round(genuine_count / total, 4),
        authenticity_breakdown=breakdown("authenticity"),
        bot_likelihood_breakdown=breakdown("bot_likelihood"),
        political_breakdown=breakdown("political_inclination"),
        relevance_breakdown=breakdown("relevance"),
        type_breakdown=breakdown("comment_type"),
        language_breakdown=breakdown("language"),
        manual_review_count=manual_count,
    )
