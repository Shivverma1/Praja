"""
routers/audience.py — Audience estimate endpoint
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.database import get_db
from backend.models import Creator
from backend.schemas import AudienceEstimateOut

router = APIRouter(prefix="/api/creator", tags=["audience"])


@router.get("/{handle}/audience", response_model=AudienceEstimateOut)
async def get_audience(handle: str, db: AsyncSession = Depends(get_db)):
    """Get audience estimate for a creator."""
    handle = handle.lower().strip().lstrip("@")
    result = await db.execute(
        select(Creator)
        .where(Creator.handle == handle)
        .options(selectinload(Creator.audience_estimate))
    )
    creator = result.scalar_one_or_none()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found.")
    if not creator.audience_estimate:
        raise HTTPException(status_code=404, detail="Audience estimate not yet computed.")
    return AudienceEstimateOut.model_validate(creator.audience_estimate)
