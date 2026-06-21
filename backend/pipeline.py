"""
pipeline.py — Full scrape → store → classify → metrics → audience pipeline
Runs as a FastAPI BackgroundTask
"""
import asyncio
import json
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.database import AsyncSessionLocal
from backend.models import Creator, Post, Comment, CommentClassification
from backend.services.instagram import fetch_creator_data
from backend.services.classifier import classify_comments
from backend.services.metrics import compute_and_store_metrics
from backend.services.audience_estimator import compute_and_store_audience


async def _update_progress(session: AsyncSession, creator: Creator, progress: int, message: str, status: str = "running"):
    creator.pipeline_progress = progress
    creator.pipeline_message = message
    creator.pipeline_status = status
    await session.commit()


async def run_pipeline(handle: str):
    """Full analysis pipeline. Runs in background."""
    async with AsyncSessionLocal() as session:
        try:
            # ── 1. Get or create creator record ─────────────────────────────
            result = await session.execute(
                select(Creator)
                .where(Creator.handle == handle.lower().strip())
                .options(selectinload(Creator.posts))
            )
            creator = result.scalar_one_or_none()
            if not creator:
                creator = Creator(handle=handle.lower().strip())
                session.add(creator)
                await session.commit()
                await session.refresh(creator)

            await _update_progress(session, creator, 5, "Fetching Instagram profile...", "running")

            # ── 2. Fetch data from Instagram (or demo) ────────────────────
            data = await fetch_creator_data(handle)
            profile = data["profile"]
            posts_data = data["posts"]

            # Update creator fields
            creator.display_name = profile.get("display_name")
            creator.profile_pic_url = profile.get("profile_pic_url")
            creator.bio = profile.get("bio")
            creator.external_link = profile.get("external_link")
            creator.verified = profile.get("verified", False)
            creator.follower_count = profile.get("follower_count", 0)
            creator.following_count = profile.get("following_count", 0)
            creator.post_count = profile.get("post_count", 0)
            creator.fetched_at = datetime.utcnow()
            await session.commit()

            await _update_progress(session, creator, 20, f"Fetched profile. Processing {len(posts_data)} posts...")

            # ── 3. Store posts ─────────────────────────────────────────────
            # Remove old posts
            for old_post in creator.posts:
                await session.delete(old_post)
            await session.flush()

            stored_posts: list[Post] = []
            for i, post_data in enumerate(posts_data):
                post = Post(
                    creator_id=creator.id,
                    shortcode=post_data.get("shortcode"),
                    post_type=post_data.get("post_type", "personal"),
                    thumbnail_url=post_data.get("thumbnail_url"),
                    caption=post_data.get("caption"),
                    hashtags=json.dumps(post_data.get("hashtags", [])),
                    likes=post_data.get("likes", 0),
                    comments_count=post_data.get("comments_count", 0),
                    shares=post_data.get("shares", 0),
                    saves=post_data.get("saves", 0),
                    posted_at=datetime.fromisoformat(post_data["posted_at"]) if post_data.get("posted_at") else None,
                    is_collaboration=post_data.get("is_collaboration", False),
                )
                session.add(post)
                await session.flush()  # get post.id

                # Store comments (raw, before classification)
                for comment_data in post_data.get("comments", []):
                    comment = Comment(
                        post_id=post.id,
                        text=comment_data.get("text", ""),
                        username=comment_data.get("username"),
                        commented_at=datetime.fromisoformat(comment_data["commented_at"]) if comment_data.get("commented_at") else None,
                    )
                    session.add(comment)
                    await session.flush()

                    # If pre-classified (demo mode), store classification directly
                    pre = comment_data.get("_pre_classified")
                    if pre:
                        clf = CommentClassification(
                            comment_id=comment.id,
                            authenticity=pre.get("authenticity"),
                            bot_likelihood=pre.get("bot_likelihood"),
                            political_inclination=pre.get("political_inclination"),
                            relevance=pre.get("relevance"),
                            comment_type=pre.get("comment_type"),
                            language=pre.get("language"),
                            requires_manual_review=pre.get("requires_manual_review", False),
                        )
                        session.add(clf)

                stored_posts.append((post, post_data.get("comments", [])))

                progress_val = 20 + int((i + 1) / len(posts_data) * 30)
                await _update_progress(session, creator, progress_val, f"Stored post {i+1}/{len(posts_data)}...")

            await session.commit()

            await _update_progress(session, creator, 55, "Classifying comments with AI...")

            # ── 4. Classify comments (only those without pre-classification) ─
            # Re-fetch creator with posts/comments
            result2 = await session.execute(
                select(Creator)
                .where(Creator.id == creator.id)
                .options(
                    selectinload(Creator.posts)
                    .selectinload(Post.comments)
                    .selectinload(Comment.classification)
                )
            )
            creator_full = result2.scalar_one()

            unclassified_comments = []
            for post in creator_full.posts:
                for comment in post.comments:
                    if not comment.classification:
                        unclassified_comments.append(comment)

            if unclassified_comments:
                # Classify in batches
                comment_dicts = [{"text": c.text} for c in unclassified_comments]
                classified = await classify_comments(comment_dicts)

                for comment, clf_data in zip(unclassified_comments, classified):
                    clf = CommentClassification(
                        comment_id=comment.id,
                        authenticity=clf_data.get("authenticity"),
                        bot_likelihood=clf_data.get("bot_likelihood"),
                        political_inclination=clf_data.get("political_inclination"),
                        relevance=clf_data.get("relevance"),
                        comment_type=clf_data.get("comment_type"),
                        language=clf_data.get("language"),
                        requires_manual_review=clf_data.get("requires_manual_review", False),
                    )
                    session.add(clf)
                await session.commit()

            await _update_progress(session, creator, 75, "Computing engagement metrics...")

            # ── 5. Compute metrics ─────────────────────────────────────────
            # Re-fetch with full relationships
            result3 = await session.execute(
                select(Creator)
                .where(Creator.id == creator.id)
                .options(selectinload(Creator.posts))
            )
            creator_metrics = result3.scalar_one()
            await compute_and_store_metrics(creator_metrics, session)

            await _update_progress(session, creator, 88, "Estimating audience demographics...")

            # ── 6. Audience estimation ─────────────────────────────────────
            result4 = await session.execute(
                select(Creator)
                .where(Creator.id == creator.id)
                .options(
                    selectinload(Creator.posts)
                    .selectinload(Post.comments)
                    .selectinload(Comment.classification)
                )
            )
            creator_audience = result4.scalar_one()
            await compute_and_store_audience(creator_audience, session)

            # ── 7. Mark complete ──────────────────────────────────────────
            await _update_progress(session, creator, 100, "Analysis complete! 🎉", "complete")

        except Exception as e:
            import traceback
            traceback.print_exc()
            async with AsyncSessionLocal() as err_session:
                err_result = await err_session.execute(
                    select(Creator).where(Creator.handle == handle.lower().strip())
                )
                err_creator = err_result.scalar_one_or_none()
                if err_creator:
                    err_creator.pipeline_status = "error"
                    err_creator.pipeline_message = f"Error: {str(e)}"
                    await err_session.commit()
