"""
services/instagram.py — Instagram data fetcher with demo fallback
"""
import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Any

import httpx

from backend.database import settings

# ─── Collaboration detection keywords ────────────────────────────────────────
COLLAB_KEYWORDS = [
    "#ad", "#sponsored", "#collab", "#paid", "#gifted", "#partnership",
    "#brandambassador", "#promo", "#advertisement", "paid partnership",
    "in collaboration with", "sponsored by",
]


def _is_collab(caption: str) -> bool:
    if not caption:
        return False
    low = caption.lower()
    return any(kw in low for kw in COLLAB_KEYWORDS)


# ─── Demo data generator ─────────────────────────────────────────────────────

DEMO_COMMENTS_POOL = [
    # English genuine
    ("omg this is amazing! love your content 😍", "user_alex23", "Genuine", "Human", "Neutral", "On-topic", "Praise", "English"),
    ("Can you share the recipe? Looks delicious!", "foodie_priya", "Genuine", "Human", "Neutral", "On-topic", "Question", "English"),
    ("This is so inspiring, you motivate me every day!", "sunshine_rita", "Genuine", "Human", "Neutral", "On-topic", "Praise", "English"),
    ("Not a fan of this one tbh 😐", "honest_review99", "Genuine", "Human", "Neutral", "On-topic", "Criticism", "English"),
    ("Tag me when you post next! @bestiee", "bestfriend_neha", "Genuine", "Human", "Neutral", "Off-topic", "Tag-a-friend", "English"),
    ("Where did you get that outfit from?", "fashionista_2k", "Genuine", "Human", "Neutral", "On-topic", "Question", "English"),
    ("Wow the editing on this is fire 🔥", "creator_vibes", "Genuine", "Human", "Neutral", "On-topic", "Praise", "English"),
    # Hindi
    ("bahut accha hai yaar ❤️", "desi_fan88", "Genuine", "Human", "Neutral", "On-topic", "Praise", "Hindi"),
    ("kya scene hai bhai 😂😂", "comedy_fan_ram", "Genuine", "Human", "Neutral", "On-topic", "Praise", "Hindi"),
    ("aaj ka content best tha!", "hindi_lover", "Genuine", "Human", "Neutral", "On-topic", "Praise", "Hindi"),
    # Hinglish (ambiguous)
    ("bhai tera content ekdum mast hai really loved it!", "hinglish_user1", "Genuine", "Human", "Neutral", "On-topic", "Praise", "Hinglish"),
    ("yaar this is so good I can't even 😭", "desi_vibe_check", "Genuine", "Human", "Neutral", "On-topic", "Praise", "Hinglish"),
    # Spam
    ("Follow me back I follow everyone! 🙏🙏", "follow4follow_bot", "Spam", "Likely-bot", "Neutral", "Off-topic", "Sales-or-promo", "English"),
    ("😍😍😍😍😍😍😍😍😍😍😍😍", "emoji_spammer", "Spam", "Likely-bot", "Neutral", "Off-topic", "Other", "English"),
    ("Check my profile for free followers!!! Link in bio!", "spam_bot_123", "Spam", "Likely-bot", "Neutral", "Off-topic", "Sales-or-promo", "English"),
    ("Nice nice nice nice nice", "repeat_bot_77", "Spam", "Likely-bot", "Neutral", "Off-topic", "Other", "English"),
    ("Buy followers cheap DM me", "promo_account", "Spam", "Likely-bot", "Neutral", "Off-topic", "Sales-or-promo", "English"),
    # Political
    ("This government is ruining everything, we need change!", "political_acc1", "Genuine", "Human", "Negative", "Off-topic", "Other", "English"),
    ("BJP is doing great work for India 🇮🇳", "bjp_supporter", "Genuine", "Human", "Positive", "Off-topic", "Other", "English"),
    ("Politics aside, great content!", "neutral_watcher", "Genuine", "Human", "Neutral", "On-topic", "Praise", "English"),
    # More genuine
    ("This video changed my perspective 🙌", "mindset_seeker", "Genuine", "Human", "Neutral", "On-topic", "Praise", "English"),
    ("When is your next post coming?", "waiting_fan", "Genuine", "Human", "Neutral", "On-topic", "Question", "English"),
    ("Shared this with my whole family!", "family_sharma", "Genuine", "Human", "Neutral", "On-topic", "Praise", "English"),
    ("Could be better honestly 🤔", "constructive_critic", "Genuine", "Human", "Neutral", "On-topic", "Criticism", "English"),
]

HASHTAG_POOL = [
    "#lifestyle", "#fashion", "#india", "#mumbai", "#trending",
    "#reels", "#viral", "#instagood", "#motivation", "#travel",
    "#food", "#fitness", "#beauty", "#skincare", "#ootd",
    "#bollywood", "#desi", "#creator", "#influencer", "#collab",
]

CAPTIONS_POOL = [
    "Living my best life 🌟 #lifestyle #india",
    "New collab alert! 🎉 So excited to partner with @brandxyz #ad #sponsored",
    "Sunday vibes ☕ #weekend #chill #mood",
    "Tried this amazing recipe today 🍛 #food #cooking #homemade",
    "Gym day 💪 consistency is key! #fitness #gym #motivation",
    "Travel diary: Goa edition 🌊 #travel #goa #vacation",
    "Paid partnership with @beautyco ✨ #gifted #beauty #skincare",
    "Just a regular day in my life 😅 #vlog #dayinmylife",
    "Obsessed with this outfit 👗 #fashion #ootd #style",
    "Books, chai, and chill 📚 #reader #lifestyle",
    "New reel out now! Drop a ❤️ if you relate #relatable #reels",
    "In collaboration with @techbrand — full review in bio link! #collab #tech",
]


def _gen_demo_comments(n: int = 15) -> list[dict]:
    selected = random.sample(DEMO_COMMENTS_POOL, min(n, len(DEMO_COMMENTS_POOL)))
    result = []
    for i, (text, username, auth, bot, pol, rel, ctype, lang) in enumerate(selected):
        result.append({
            "text": text,
            "username": username,
            "commented_at": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
            "_pre_classified": {
                "authenticity": auth,
                "bot_likelihood": bot,
                "political_inclination": pol,
                "relevance": rel,
                "comment_type": ctype,
                "language": lang,
                "requires_manual_review": lang == "Hinglish",
            }
        })
    return result


def _gen_post(idx: int, follower_count: int) -> dict:
    is_collab = idx in [2, 6, 11]
    caption = CAPTIONS_POOL[idx % len(CAPTIONS_POOL)]
    if is_collab and "#ad" not in caption and "#collab" not in caption:
        caption = caption.rstrip() + " #ad #partnership"
    hashtags = random.sample(HASHTAG_POOL, random.randint(3, 7))
    base_likes = int(follower_count * random.uniform(0.03, 0.12))
    return {
        "shortcode": f"DEMO{idx:03d}",
        "post_type": "collab" if is_collab else "personal",
        "thumbnail_url": f"https://picsum.photos/seed/post{idx}/400/400",
        "caption": caption,
        "hashtags": hashtags,
        "likes": base_likes + random.randint(-500, 500),
        "comments_count": int(base_likes * random.uniform(0.05, 0.15)),
        "shares": int(base_likes * random.uniform(0.01, 0.05)),
        "saves": int(base_likes * random.uniform(0.02, 0.08)),
        "posted_at": (datetime.now() - timedelta(days=idx * 3)).isoformat(),
        "is_collaboration": is_collab,
        "comments": _gen_demo_comments(random.randint(10, 20)),
    }


DEMO_PROFILES: dict[str, dict] = {
    "_default": {
        "handle": "demo_creator",
        "display_name": "Priya Sharma",
        "profile_pic_url": "https://picsum.photos/seed/priya/200/200",
        "bio": "✨ Lifestyle & Fashion | Mumbai 🌸 Brand Collabs: priya@email.com",
        "external_link": "https://linktr.ee/priyasharma",
        "verified": False,
        "follower_count": 485000,
        "following_count": 892,
        "post_count": 347,
    }
}


async def fetch_creator_data(handle: str) -> dict[str, Any]:
    """
    Returns profile dict + list of 12 posts (each with comments).
    Priority: Live Instagram API → RapidAPI → Demo mode.
    """
    mode = settings.APP_MODE

    if mode == "live" and settings.INSTAGRAM_ACCESS_TOKEN:
        try:
            result = await _fetch_live_instagram(handle)
            print(f"[instagram] Live fetch SUCCESS for {handle}")
            return result
        except Exception as exc:
            import traceback
            print(f"[instagram] Live fetch FAILED for {handle}: {exc}")
            traceback.print_exc()

    if mode == "live" and settings.RAPIDAPI_KEY:
        try:
            return await _fetch_rapidapi(handle)
        except Exception as exc:
            print(f"[instagram] RapidAPI fetch failed ({exc}), falling back to demo")

    return _fetch_demo(handle)


# ─── Live Instagram Graph API ─────────────────────────────────────────────────

async def _fetch_live_instagram(handle: str) -> dict:
    """Uses Instagram Business Discovery API to fetch public profile."""
    base = "https://graph.facebook.com/v19.0"
    token = settings.INSTAGRAM_ACCESS_TOKEN
    ig_id = settings.INSTAGRAM_BUSINESS_ACCOUNT_ID

    async with httpx.AsyncClient(timeout=30) as client:
        # Step 1: Get target user ID via Business Discovery
        fields = (
            "business_discovery.as(target){id,username,name,biography,"
            "profile_picture_url,followers_count,follows_count,media_count,"
            "website,is_verified}"
        )
        url = (
            f"{base}/{ig_id}"
            f"?fields={fields}"
            f"&username={handle}"
            f"&access_token={token}"
        )
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()["business_discovery"]

        profile = {
            "handle": data.get("username", handle),
            "display_name": data.get("name"),
            "profile_pic_url": data.get("profile_picture_url"),
            "bio": data.get("biography"),
            "external_link": data.get("website"),
            "verified": data.get("is_verified", False),
            "follower_count": data.get("followers_count", 0),
            "following_count": data.get("follows_count", 0),
            "post_count": data.get("media_count", 0),
        }
        target_id = data["id"]

        # Step 2: Fetch last 12 media
        r2 = await client.get(
            f"{base}/{target_id}/media",
            params={
                "fields": "id,shortcode,media_type,thumbnail_url,media_url,caption,"
                          "like_count,comments_count,timestamp",
                "limit": 12,
                "access_token": token,
            }
        )
        r2.raise_for_status()
        media_list = r2.json().get("data", [])

        posts = []
        for media in media_list:
            caption = media.get("caption", "")
            hashtags = [w for w in caption.split() if w.startswith("#")] if caption else []
            # Fetch comments (up to 50)
            comments = []
            try:
                r3 = await client.get(
                    f"{base}/{media['id']}/comments",
                    params={"fields": "id,text,username,timestamp", "limit": 50, "access_token": token}
                )
                comments = [
                    {"text": c["text"], "username": c.get("username"), "commented_at": c.get("timestamp")}
                    for c in r3.json().get("data", [])
                ]
            except Exception:
                pass

            posts.append({
                "shortcode": media.get("shortcode"),
                "post_type": "collab" if _is_collab(caption) else "personal",
                "thumbnail_url": media.get("thumbnail_url") or media.get("media_url"),
                "caption": caption,
                "hashtags": hashtags,
                "likes": media.get("like_count", 0),
                "comments_count": media.get("comments_count", 0),
                "shares": 0,
                "saves": 0,
                "posted_at": media.get("timestamp"),
                "is_collaboration": _is_collab(caption),
                "comments": comments,
            })

    return {"profile": profile, "posts": posts}


# ─── RapidAPI fallback ────────────────────────────────────────────────────────

async def _fetch_rapidapi(handle: str) -> dict:
    """Fallback: RapidAPI Instagram Scraper Stable API."""
    base_url = "https://instagram-scraper-stable-api.p.rapidapi.com"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": "instagram-scraper-stable-api.p.rapidapi.com",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    def _parse_media(media: dict) -> dict:
        node = media.get("node", media)
        caption_node = node.get("caption") or {}
        caption = caption_node.get("text", "") if isinstance(caption_node, dict) else str(caption_node)
        hashtags = [w for w in caption.split() if w.startswith("#")]
        is_collab = _is_collab(caption) or node.get("is_paid_partnership", False)
        thumbnail = (node.get("image_versions2", {}).get("candidates", [{}]) or [{}])[0].get("url")
        return {
            "shortcode": node.get("code"),
            "post_type": "collab" if is_collab else "personal",
            "thumbnail_url": thumbnail,
            "caption": caption,
            "hashtags": hashtags,
            "likes": node.get("like_count", 0),
            "comments_count": node.get("comment_count", 0),
            "shares": 0,
            "saves": node.get("save_count", 0),
            "posted_at": datetime.fromtimestamp(node.get("taken_at", 0)).isoformat() if node.get("taken_at") else None,
            "is_collaboration": is_collab,
            "comments": [],
        }

    async with httpx.AsyncClient(timeout=30) as client:
        # Fetch profile (retry once on 429)
        for attempt in range(2):
            r = await client.post(
                f"{base_url}/ig_get_fb_profile.php",
                data={"username_or_url": handle, "data": "basic"},
                headers=headers,
            )
            if r.status_code == 429:
                await asyncio.sleep(3)
                continue
            break
        r.raise_for_status()
        raw = r.json().get("data", r.json())

        profile = {
            "handle": raw.get("username", handle),
            "display_name": raw.get("full_name") or raw.get("name"),
            "profile_pic_url": raw.get("hd_profile_pic_url_info", {}).get("url") or raw.get("profile_pic_url"),
            "bio": raw.get("biography"),
            "external_link": raw.get("external_url"),
            "verified": raw.get("is_verified", False),
            "follower_count": raw.get("follower_count", 0),
            "following_count": raw.get("following_count", 0),
            "post_count": raw.get("media_count", 0),
        }

        # Fetch posts sequentially to avoid rate limiting
        all_media = []

        posts_r = await client.post(f"{base_url}/get_ig_user_posts.php",
            data={"username_or_url": handle, "amount": "8", "pagination_token": ""},
            headers=headers)
        all_media.extend(posts_r.json().get("posts", []))

        await asyncio.sleep(1)

        try:
            reels_r = await client.post(f"{base_url}/get_ig_user_reels.php",
                data={"username_or_url": handle, "amount": "4", "pagination_token": ""},
                headers=headers)
            all_media.extend(reels_r.json().get("reels", []))
        except Exception:
            pass

        parsed_posts = [
            _parse_media(m) for m in all_media[:12]
            if m.get("node", m).get("like_count") is not None
        ]

        # Fetch comments sequentially with delay to avoid rate limits
        get_headers = {
            "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
            "X-RapidAPI-Host": "instagram-scraper-stable-api.p.rapidapi.com",
        }
        for post in parsed_posts[:6]:  # only first 6 posts to save quota
            code = post.get("shortcode")
            if not code:
                continue
            try:
                await asyncio.sleep(0.5)
                cr = await client.get(
                    f"{base_url}/get_post_comments.php",
                    params={"media_code": code, "sort_order": "popular"},
                    headers=get_headers,
                )
                raw_comments = cr.json().get("comments", [])
                post["comments"] = [
                    {
                        "text": c.get("text", ""),
                        "username": c.get("owner", {}).get("username", "") if isinstance(c.get("owner"), dict) else "",
                        "commented_at": datetime.fromtimestamp(c["created_at"]).isoformat() if c.get("created_at") else None,
                    }
                    for c in raw_comments[:10]
                ]
            except Exception:
                continue

    return {"profile": profile, "posts": parsed_posts}


# ─── Demo mode ────────────────────────────────────────────────────────────────

def _fetch_demo(handle: str) -> dict:
    rng = random.Random(hash(handle) % (2**32))
    follower_count = rng.randint(50_000, 2_000_000)
    profile = {
        "handle": handle,
        "display_name": handle.replace("_", " ").title(),
        "profile_pic_url": f"https://picsum.photos/seed/{handle}/200/200",
        "bio": f"✨ Content Creator | Sharing {rng.choice(['lifestyle', 'fashion', 'food', 'tech', 'fitness'])} vibes 🌸 DM for collabs",
        "external_link": f"https://linktr.ee/{handle}",
        "verified": rng.random() > 0.8,
        "follower_count": follower_count,
        "following_count": rng.randint(200, 2000),
        "post_count": rng.randint(50, 500),
    }
    posts = []
    for i in range(12):
        p = _gen_post(i, follower_count)
        p["shortcode"] = f"{handle[:4].upper()}{i:03d}"
        p["thumbnail_url"] = f"https://picsum.photos/seed/{handle}post{i}/400/400"
        posts.append(p)

    return {"profile": profile, "posts": posts}
