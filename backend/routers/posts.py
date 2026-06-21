"""
routers/posts.py — Post and comment endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.database import get_db
from backend.models import Creator, Post, Comment
from backend.schemas import PostOut, CommentOut

router = APIRouter(prefix="/api/creator", tags=["posts"])


@router.get("/{handle}/posts", response_model=list[PostOut])
async def get_posts(handle: str, db: AsyncSession = Depends(get_db)):
    """Get all 12 recent posts for a creator."""
    handle = handle.lower().strip().lstrip("@")
    result = await db.execute(
        select(Creator).where(Creator.handle == handle).options(selectinload(Creator.posts))
    )
    creator = result.scalar_one_or_none()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found.")
    # Sort by posted_at desc
    posts = sorted(creator.posts, key=lambda p: p.posted_at.timestamp() if p.posted_at else p.id, reverse=True)
    return [PostOut.model_validate(p) for p in posts]


@router.get("/{handle}/posts/{post_id}/comments", response_model=list[CommentOut])
async def get_post_comments(handle: str, post_id: int, db: AsyncSession = Depends(get_db)):
    """Get all classified comments for a specific post."""
    handle = handle.lower().strip().lstrip("@")
    result = await db.execute(
        select(Post)
        .join(Creator)
        .where(Creator.handle == handle, Post.id == post_id)
        .options(
            selectinload(Post.comments).selectinload(Comment.classification)
        )
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    return [CommentOut.model_validate(c) for c in post.comments]
