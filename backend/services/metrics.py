"""
services/metrics.py — Engagement metrics computation
"""
import json
from collections import Counter

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models import Creator, Post, EngagementMetrics


COLLAB_KEYWORDS = [
    "#ad", "#sponsored", "#collab", "#paid", "#gifted", "#partnership",
    "#brandambassador", "#promo", "#advertisement", "paid partnership",
    "in collaboration with", "sponsored by",
]


async def compute_and_store_metrics(creator: Creator, session: AsyncSession) -> EngagementMetrics:
    """Compute engagement metrics for a creator from their stored posts."""
    posts = creator.posts

    if not posts:
        return None

    total_likes = sum(p.likes for p in posts)
    total_comments = sum(p.comments_count for p in posts)
    total_shares = sum(p.shares for p in posts)
    total_saves = sum(p.saves for p in posts)
    n = len(posts)

    avg_likes = total_likes / n
    avg_comments = total_comments / n
    avg_shares = total_shares / n
    avg_saves = total_saves / n

    # Engagement Rate = (avg_likes + avg_comments + avg_saves) / follower_count * 100
    follower_count = max(creator.follower_count, 1)
    engagement_rate = (avg_likes + avg_comments + avg_saves) / follower_count * 100

    # Top hashtags
    hashtag_counter: Counter = Counter()
    for post in posts:
        for tag in post.hashtag_list:
            hashtag_counter[tag.lower()] += 1
    top_hashtags = [{"tag": tag, "count": count} for tag, count in hashtag_counter.most_common(15)]

    # Most recent collab post
    collab_posts = [p for p in posts if p.is_collaboration]
    collab_post_id = None
    if collab_posts:
        most_recent_collab = max(collab_posts, key=lambda p: p.posted_at or p.id)
        collab_post_id = most_recent_collab.id

    # Delete existing metrics if any
    existing = await session.execute(
        select(EngagementMetrics).where(EngagementMetrics.creator_id == creator.id)
    )
    existing_row = existing.scalar_one_or_none()
    if existing_row:
        await session.delete(existing_row)
        await session.flush()

    metrics = EngagementMetrics(
        creator_id=creator.id,
        avg_likes=round(avg_likes, 2),
        avg_comments=round(avg_comments, 2),
        avg_shares=round(avg_shares, 2),
        avg_saves=round(avg_saves, 2),
        engagement_rate=round(engagement_rate, 4),
        top_hashtags=json.dumps(top_hashtags),
        collab_post_id=collab_post_id,
    )
    session.add(metrics)
    await session.commit()
    await session.refresh(metrics)
    return metrics
