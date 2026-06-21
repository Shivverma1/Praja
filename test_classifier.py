import asyncio, sys
sys.path.insert(0, '.')
from backend.services.classifier import classify_comments

test_comments = [
    # SHORT comments (previous tests)
    {"text": "wow so original", "username": "u1"},
    {"text": "Love it but the price is bad", "username": "u2"},

    # LONG comments
    {"text": "The intro was absolutely amazing and I loved the editing. The music choice was perfect and really matched the vibe. But the ending was really disappointing and felt very rushed.", "username": "u3"},

    {"text": "I have been following you for 3 years now. Your content has always been top notch and every video is better than the last. You are honestly one of the best creators out there. Keep it up!", "username": "u4"},

    {"text": "Honestly this video had so much potential. The first half was great, loved the concept. But the second half completely fell apart. The sound quality was terrible and the editing was lazy. Would not recommend.", "username": "u5"},

    {"text": "Oh WOW what a creative idea. Never seen anyone do this before. So original. Totally groundbreaking stuff here.", "username": "u6"},

    {"text": "The content is good but I have a question. Where did you buy that outfit? Also what camera do you use? And how long does it take to edit one video?", "username": "u7"},

    {"text": "This was incredible! The way you explained everything step by step was so helpful. I have tried so many tutorials before but none of them worked for me. Yours actually did! Thank you so much for making this.", "username": "u8"},
]

results = asyncio.run(classify_comments(test_comments))
print(f"{'Comment (truncated)':<52} | {'Type':<15} | {'Auth':<8} | Sarcasm | Mixed | Sentences")
print("-" * 115)
for r in results:
    display = r['text'].encode('ascii', errors='replace').decode('ascii')[:51]
    sarcasm = str(r.get("_is_sarcasm", False))
    mixed   = str(r.get("_is_mixed", False))
    sents   = str(r.get("_sentence_count", 1))
    print(f"{display:<52} | {r['comment_type']:<15} | {r['authenticity']:<8} | {sarcasm:<7} | {mixed:<5} | {sents}")
