"""
services/classifier.py — Enhanced rule-based + VADER comment classifier
Handles: sarcasm, mixed intent, ambiguous comments, Hinglish, bot detection.
Fully offline — no external AI API required.
"""
import re
from collections import Counter

# ── VADER Sentiment (social-media-aware, handles 🙄 / CAPS / punctuation) ───
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _vader = SentimentIntensityAnalyzer()
    VADER_AVAILABLE = True
except ImportError:
    _vader = None
    VADER_AVAILABLE = False

# ── Optional langdetect ───────────────────────────────────────────────────────
try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


# ─── Keyword dictionaries ─────────────────────────────────────────────────────

SPAM_PATTERNS = [
    r'follow\s*(me|back|4|for)',
    r'f(ollow)?4f(ollow)?',
    r'follow\s*everyone',
    r'(dm|message)\s*me\b',
    r'free\s*followers',
    r'buy\s*(followers|likes)',
    r'check\s*(my|out\s*my)\s*(profile|page|bio)',
    r'click\s*(the\s*)?(link|here)',
    r'http[s]?://',
    r'link\s*in\s*(my\s*)?bio',
    r'earn\s*money',
    r'(\d+)\s*(followers|likes)\s*(in|within)',
]
SPAM_REGEX = [re.compile(p, re.IGNORECASE) for p in SPAM_PATTERNS]

EMOJI_ONLY_RE = re.compile(
    r'^[\U0001F300-\U0001FFFF\U00002700-\U000027BF\U0000FE00-\U0000FEFF'
    r'\U00002600-\U000026FF\s!.?,😀-🙏]+$'
)

BOT_USERNAME_RE = re.compile(
    r'(bot|follow|promo|spam|fake|buy|free|earn|money|gain|like4like)',
    re.IGNORECASE
)

# ── Sarcasm signals ───────────────────────────────────────────────────────────
SARCASM_EMOJIS = {"🙄", "😒", "😏", "🤡", "💀", "😑", "🤨", "😐"}
SARCASM_PHRASES = re.compile(
    r'\b(wow\s+so|oh\s+wow|oh\s+sure|oh\s+yeah|totally|right\.\.\.|'
    r'sure\.\.\.|definitely\.\.\.|absolutely|as\s+if|yeah\s+right|'
    r'oh\s+really|how\s+original|so\s+clever|great\s+job\s+🙄|'
    r'thanks\s+for\s+nothing)\b',
    re.IGNORECASE
)

# ── Hindi/Hinglish ────────────────────────────────────────────────────────────
HINDI_WORDS = {
    "yaar", "bhai", "bahut", "accha", "theek", "kya", "hai", "nahi", "aur",
    "main", "mera", "tera", "tum", "hum", "woh", "karo", "karna", "sahi",
    "sundar", "mazaa", "aacha", "ekdum", "bilkul", "zaroor", "bohot",
    "zyada", "thoda", "phir", "abhi", "aaj", "kal", "dil", "pyar", "dost",
    "yaad", "bahot", "samjha", "dekho", "scene", "mast", "bindas",
    "maza", "zabardast", "shaandaar", "waah", "wah", "arrey", "arre",
    "haan", "naa", "bas", "lekin", "par", "toh", "bhi", "sirf",
    "kuch", "sab", "log", "din", "raat", "ghar", "kam", "zyada",
}

# ── Political ─────────────────────────────────────────────────────────────────
POLITICAL_TRIGGERS = [
    "government", "politics", "election", "party", "vote", "minister",
    "pm ", "cm ", "bjp", "congress", "aap ", "nda", "upa", "modi",
    "rahul", "kejriwal", "yogi", "mamata", "parliament", "lok sabha",
    "sarkar", "neta", "desh",
]
POLITICAL_POSITIVE_WORDS = [
    "good government", "great work", "positive change", "doing well",
    "best pm", "great leader", "development", "vikas", "jai hind",
]
POLITICAL_NEGATIVE_WORDS = [
    "bad government", "incompetent", "corrupt", "scam", "fraud",
    "protest", "resign", "failure", "loot", "worst government", "pathetic",
    "dictatorship", "thief", "chor",
]

# ── Comment type ──────────────────────────────────────────────────────────────
PRAISE_WORDS = {
    "love", "amazing", "great", "beautiful", "awesome", "fire", "best",
    "omg", "incredible", "fantastic", "wonderful", "perfect", "brilliant",
    "superb", "excellent", "outstanding", "gorgeous", "stunning", "wow",
    # Hindi/Hinglish praise
    "waah", "wah", "zabardast", "shaandaar", "mast", "ekdum", "bindas",
    "accha", "aacha", "sundar", "mazaa", "maza", "badhiya", "jhakaas",
    # English slang
    "nice", "good", "cute", "pretty", "dope", "lit", "goat", "legend",
    "class", "top", "obsessed", "blessed", "goals", "flawless",
}
CRITICISM_WORDS = {
    "bad", "terrible", "hate", "worst", "not good", "disappointed",
    "boring", "ugly", "pathetic", "cringe", "trash", "waste", "useless",
    "overrated", "fake", "annoying", "awful", "horrible", "disgusting",
    "disappointing", "lame", "mediocre", "poor quality", "regret",
}
CONTRAST_CONJUNCTIONS = {"but", "however", "although", "though", "except",
                          "despite", "yet", "still", "while", "whereas"}
QUESTION_STARTERS = {"how", "what", "when", "where", "who", "why", "which",
                      "can", "could", "would", "should", "is", "are", "do",
                      "does", "did"}
SALES_WORDS = {
    "buy", "sell", "offer", "sale", "discount", "deal", "shop", "order",
    "price", "cheap", "brand", "product", "available", "contact",
    "purchase", "wholesale", "reseller",
}


# ─── Detection functions ──────────────────────────────────────────────────────

def _vader_score(text: str) -> float:
    """Returns VADER compound score -1.0 (negative) to +1.0 (positive)."""
    if VADER_AVAILABLE and _vader:
        return _vader.polarity_scores(text)["compound"]
    return 0.0


def _detect_spam(text: str) -> bool:
    if EMOJI_ONLY_RE.match(text.strip()) and len(text.strip()) < 25:
        return True
    if len(text.strip()) < 6 and re.match(r'^[!.😂❤️💯🔥]+$', text.strip()):
        return True
    words = text.lower().split()
    if len(words) >= 4:
        freq = Counter(words)
        if freq.most_common(1)[0][1] >= len(words) * 0.7:
            return True
    for pattern in SPAM_REGEX:
        if pattern.search(text):
            return True
    return False


def _detect_bot(is_spam: bool, text: str, username: str = "") -> str:
    score = 0
    if is_spam:
        score += 2
    if username and BOT_USERNAME_RE.search(username):
        score += 2
    if EMOJI_ONLY_RE.match(text.strip()):
        score += 1
    if len(text.strip()) <= 3:
        score += 1
    return "Likely-bot" if score >= 3 else "Uncertain" if score >= 1 else "Human"


def _detect_sarcasm(text: str, compound: float) -> bool:
    """
    Detect sarcasm by combining multiple signals:
    1. Sarcasm emojis paired with positive words
    2. VADER says negative but positive words used
    3. Known sarcasm phrases
    4. ALL CAPS positive words in negative context
    """
    text_lower = text.lower()
    has_sarcasm_emoji = any(e in text for e in SARCASM_EMOJIS)
    has_praise = any(w in text_lower for w in PRAISE_WORDS)

    # Signal 1: sarcasm emoji + positive word
    if has_sarcasm_emoji and has_praise:
        return True

    # Signal 2: VADER says it's negative but we see positive words (contradiction)
    if VADER_AVAILABLE and compound < -0.25 and has_praise:
        return True

    # Signal 3: known sarcasm phrases
    if SARCASM_PHRASES.search(text):
        return True

    # Signal 4: ALL CAPS positive word + sarcasm emoji
    allcaps_positive = any(w.upper() in text for w in ["WOW", "AMAZING", "GREAT", "NICE", "COOL", "SURE"])
    if allcaps_positive and has_sarcasm_emoji:
        return True

    # Signal 5: trailing ellipsis on a short positive comment = sarcasm
    if re.search(r'(nice|good|great|wow|cool|okay)\s*\.{2,}$', text_lower):
        return True

    return False


def _detect_mixed_intent(text: str) -> tuple[bool, str]:
    """
    Detect mixed-intent comments like 'Love it but the price is bad'.
    Returns (is_mixed, dominant_type).
    Strategy: the clause AFTER the contrast word (but/however) dominates.
    """
    text_lower = text.lower()
    has_praise = any(w in text_lower for w in PRAISE_WORDS)
    has_criticism = any(w in text_lower for w in CRITICISM_WORDS)

    if not (has_praise and has_criticism):
        return False, ""

    # Check for contrast conjunction
    for conj in CONTRAST_CONJUNCTIONS:
        if f" {conj} " in text_lower or text_lower.startswith(conj + " "):
            parts = re.split(rf'\b{conj}\b', text_lower, maxsplit=1, flags=re.IGNORECASE)
            if len(parts) == 2:
                after = parts[1]
                after_has_criticism = any(w in after for w in CRITICISM_WORDS)
                after_has_praise = any(w in after for w in PRAISE_WORDS)
                if after_has_criticism:
                    return True, "Criticism"
                if after_has_praise:
                    return True, "Praise"

    # No conjunction — use VADER to resolve
    compound = _vader_score(text)
    if compound >= 0.05:
        return True, "Praise"
    elif compound <= -0.05:
        return True, "Criticism"
    return True, "Other"


def _detect_language(text: str) -> tuple[str, bool]:
    devanagari = re.findall(r'[\u0900-\u097F]', text)
    has_devanagari = len(devanagari) > 3
    has_english = bool(re.search(r'\b[a-zA-Z]{3,}\b', text))
    words_lower = set(text.lower().split())
    hindi_count = len(words_lower & HINDI_WORDS)
    total_words = max(len(text.split()), 1)

    if has_devanagari and not has_english:
        return "Hindi", False
    if has_devanagari and has_english:
        return "Hinglish", True
    if hindi_count >= 2 and has_english:
        return "Hinglish", False
    if hindi_count / total_words > 0.5 and not has_english:
        return "Hindi", False

    if LANGDETECT_AVAILABLE and len(text) > 15:
        try:
            lang = detect(text)
            if lang == "hi":
                return "Hindi", False
            if lang in ("ta", "te", "kn", "ml", "bn", "gu", "pa", "mr", "or"):
                return "Regional", False
        except Exception:
            pass

    return "English", False


def _detect_political(text: str) -> str:
    text_lower = text.lower()
    if not any(t in text_lower for t in POLITICAL_TRIGGERS):
        return "N/A"
    pos = sum(1 for p in POLITICAL_POSITIVE_WORDS if p in text_lower)
    neg = sum(1 for n in POLITICAL_NEGATIVE_WORDS if n in text_lower)
    # Also use VADER for political comments
    compound = _vader_score(text)
    if compound > 0.3:
        pos += 1
    elif compound < -0.3:
        neg += 1
    if pos > neg:
        return "Positive"
    if neg > pos:
        return "Negative"
    return "Neutral"


def _detect_comment_type(text: str, is_spam: bool, is_sarcasm: bool,
                         long_analysis: dict | None = None) -> str:
    text_lower = text.lower()

    # Tag-a-friend
    if text.strip().startswith("@") or re.search(r'\s@\w+', text):
        return "Tag-a-friend"

    # Sales/promo — only if NOT a genuine question
    has_question = "?" in text
    if is_spam and any(w in text_lower for w in SALES_WORDS):
        return "Sales-or-promo"
    if not has_question and any(w in text_lower for w in {"buy", "sell", "offer", "sale", "discount", "purchase"}):
        return "Sales-or-promo"

    # Question (after sales check to avoid mis-classifying "where to buy?")
    if has_question:
        return "Question"
    first_word = text_lower.split()[0] if text_lower.split() else ""
    if first_word in QUESTION_STARTERS:
        return "Question"

    # Sarcasm → Criticism
    if is_sarcasm:
        return "Criticism"

    # Ambiguous / very short comments → Other
    stripped = text_lower.strip().rstrip('.')
    AMBIGUOUS_WORDS = {"interesting", "ok", "okay", "sure", "hmm", "hm",
                       "lol", "haha", "k", "nice", "cool", "noted"}
    if stripped in AMBIGUOUS_WORDS:
        return "Other"
    if re.match(r'^(nice|good|cool|okay|ok|interesting|sure)\.{2,}$', text_lower):
        return "Other"

    # For long comments, use the weighted sentence-level score
    if long_analysis:
        dominant_score = long_analysis["dominant_score"]
        if dominant_score >= 0.15:
            return "Praise"
        if dominant_score <= -0.15:
            return "Criticism"
        return "Other"

    # Short comment — use VADER compound directly
    compound = _vader_score(text)
    if compound >= 0.2:
        return "Praise"
    if compound <= -0.2:
        return "Criticism"

    # Keyword fallback
    if any(w in text_lower for w in PRAISE_WORDS):
        return "Praise"
    if any(w in text_lower for w in CRITICISM_WORDS):
        return "Criticism"

    return "Other"


# ─── Long comment analysis ────────────────────────────────────────────────────

SENT_SPLIT_RE = re.compile(r'(?<=[.!?])\s+|\n+')

def _analyze_long_comment(text: str) -> dict | None:
    """
    Sentence-level analysis for long comments (>120 chars / 3+ sentences).

    Strategy:
    - Split into sentences
    - Score each sentence with VADER
    - Weight the LAST sentence most (it's the conclusion / lasting impression)
    - Detect per-sentence sarcasm
    - Detect mixed-intent across sentence boundaries
    - Return a summary dict used by the main classifier

    Example:
      "The intro was amazing and I loved the editing. The music choice was
       perfect. But the ending was really disappointing and felt rushed."
      → 2 positive sentences + 1 negative (last) → Criticism dominates
    """
    # Only apply to genuinely long comments
    sentences = [s.strip() for s in SENT_SPLIT_RE.split(text) if s.strip() and len(s.strip()) > 8]
    if len(sentences) < 2 or len(text) < 120:
        return None

    # Score each sentence
    scores = [_vader_score(s) for s in sentences]
    sarcasm_flags = [_detect_sarcasm(s, sc) for s, sc in zip(sentences, scores)]

    # Weighted average: last sentence = 50%, rest split equally
    n = len(sentences)
    if n == 1:
        weights = [1.0]
    else:
        last_weight = 0.50
        other_weight = 0.50 / (n - 1)
        weights = [other_weight] * (n - 1) + [last_weight]

    dominant_score = sum(w * s for w, s in zip(weights, scores))

    # Sarcasm in any sentence flips the dominant score
    has_any_sarcasm = any(sarcasm_flags)
    if has_any_sarcasm:
        # If sarcasm detected in an otherwise positive comment, flip to negative
        sarcasm_sentence_scores = [scores[i] for i, f in enumerate(sarcasm_flags) if f]
        if sarcasm_sentence_scores and sum(sarcasm_sentence_scores) > 0:
            dominant_score -= 0.4   # penalise for sarcasm

    # Mixed intent: positive AND negative sentences both present
    has_positive_sentences = any(s > 0.2 for s in scores)
    has_negative_sentences = any(s < -0.2 for s in scores)
    is_mixed = has_positive_sentences and has_negative_sentences

    # Classify each sentence's type for the dominant-type vote
    type_votes: list[str] = []
    for sentence, sc in zip(sentences, scores):
        if "?" in sentence:
            type_votes.append("Question")
        elif sc >= 0.2:
            type_votes.append("Praise")
        elif sc <= -0.2:
            type_votes.append("Criticism")

    # Majority vote from sentences, but last sentence breaks ties
    last_sentence_type = (
        "Question" if "?" in sentences[-1]
        else "Criticism" if scores[-1] <= -0.15
        else "Praise" if scores[-1] >= 0.15
        else None
    )

    return {
        "dominant_score": dominant_score,
        "is_mixed": is_mixed,
        "has_sarcasm": has_any_sarcasm,
        "sentence_count": n,
        "scores": scores,
        "last_sentence_type": last_sentence_type,
        "type_votes": type_votes,
    }



# ─── Main entry point ─────────────────────────────────────────────────────────

async def classify_comments(comments: list[dict]) -> list[dict]:
    """
    Classify a list of comment dicts in-place.
    Fully offline — uses VADER + langdetect + rule-based logic.
    Each dict must have a 'text' key.

    Handles:
      Short comments  : keyword rules + VADER compound score
      Long comments   : sentence-level VADER + last-sentence weighting
      Sarcasm         : emoji + VADER contradiction + known phrases
      Mixed intent    : clause-after-conjunction + sentence-level split
      Ambiguous       : single-word/ellipsis → Other
      Hinglish/Hindi  : Devanagari script + Hindi word dictionary + langdetect
      Spam / Bots     : regex patterns + username signals
      Political       : keyword triggers + VADER assist
    """
    results = []
    for comment in comments:
        # Pre-classified demo data — skip reprocessing
        if comment.get("_pre_classified"):
            comment.update(comment.pop("_pre_classified"))
            results.append(comment)
            continue

        text = comment.get("text", "")
        username = comment.get("username", "")

        # ── Long comment analysis (sentence-level) ────────────────────────────
        long_analysis = _analyze_long_comment(text)

        # ── Core signals ──────────────────────────────────────────────────────
        compound = long_analysis["dominant_score"] if long_analysis else _vader_score(text)
        is_spam = _detect_spam(text)

        # Sarcasm: check full text AND flag from long analysis
        is_sarcasm = (not is_spam) and (
            _detect_sarcasm(text, compound)
            or (long_analysis is not None and long_analysis["has_sarcasm"])
        )

        # Mixed intent: short-text conjunction check OR long-text sentence split
        if long_analysis and long_analysis["is_mixed"]:
            is_mixed = True
            # Last sentence decides the dominant type
            lst = long_analysis["last_sentence_type"]
            mixed_dominant = lst if lst else ("Criticism" if compound <= 0 else "Praise")
        else:
            is_mixed, mixed_dominant = _detect_mixed_intent(text)

        # ── 1. Authenticity ───────────────────────────────────────────────────
        authenticity = "Spam" if is_spam else "Genuine"

        # ── 2. Bot likelihood ─────────────────────────────────────────────────
        bot_likelihood = _detect_bot(is_spam, text, username)

        # ── 3. Language ───────────────────────────────────────────────────────
        language, requires_manual_review = _detect_language(text)

        # ── 4. Political ──────────────────────────────────────────────────────
        political_inclination = _detect_political(text)

        # ── 5. Comment type ───────────────────────────────────────────────────
        if is_mixed:
            comment_type = mixed_dominant
        else:
            comment_type = _detect_comment_type(text, is_spam, is_sarcasm, long_analysis)

        # ── 6. Relevance ──────────────────────────────────────────────────────
        relevance = (
            "Off-topic"
            if is_spam or political_inclination in ("Positive", "Negative")
            else "On-topic"
        )

        comment.update({
            "authenticity": authenticity,
            "bot_likelihood": bot_likelihood,
            "political_inclination": political_inclination,
            "relevance": relevance,
            "comment_type": comment_type,
            "language": language,
            "requires_manual_review": requires_manual_review,
            # Debug flags (not stored in DB)
            "_is_sarcasm": is_sarcasm,
            "_is_mixed": is_mixed,
            "_sentence_count": long_analysis["sentence_count"] if long_analysis else 1,
        })
        results.append(comment)

    return results
