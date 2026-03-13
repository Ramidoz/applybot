"""Score job postings 0–100 against a master resume."""
from __future__ import annotations
import math
import re

from applybot.scraper import JobPost

# Hard-skip phrases (regex, case-insensitive)
HARD_SKIP_PATTERNS = [
    r"no\s+visa\s+sponsorship",
    r"must\s+be\s+(a\s+)?(US\s+citizen|permanent\s+resident|green\s+card\s+holder)",
    r"(US|U\.S\.)\s+citizen\s+or\s+permanent\s+resident",
    r"citizenship\s+required",
    r"security\s+clearance\s+required",
]

STOP_WORDS = {
    "the", "and", "for", "are", "this", "with", "that", "have",
    "from", "will", "our", "you", "your", "we", "be", "to", "of",
    "in", "is", "at", "as", "an", "a", "or", "on", "it",
}


def extract_keywords(text: str) -> set[str]:
    tokens = re.findall(r"[a-z][a-z+#.]{2,}", text.lower())
    return {t for t in tokens if t not in STOP_WORDS}


def _keyword_overlap_score(doc_keywords: set[str], query_keywords: set[str]) -> float:
    """Normalized keyword overlap: |intersection| / sqrt(|query|). Not full TF-IDF."""
    if not query_keywords:
        return 0.0
    overlap = doc_keywords & query_keywords
    return len(overlap) / math.sqrt(len(query_keywords))


def score_job(job: JobPost, resume_text: str) -> float:
    """Return a 0–100 score for how well the job matches the resume."""
    resume_kws = extract_keywords(resume_text)
    jd_kws = extract_keywords(job.description + " " + job.title)

    raw = _keyword_overlap_score(resume_kws, jd_kws)
    # Raw overlap for a strong match is ~0.7–0.85; * 120 maps that to 70–100 range
    score = min(100.0, raw * 120)
    return round(score, 1)


def is_hard_skip(job: JobPost) -> bool:
    """Return True if the job must be skipped due to sponsorship/citizenship restrictions."""
    text = (job.description + " " + job.title).lower()
    return any(re.search(p, text, re.IGNORECASE) for p in HARD_SKIP_PATTERNS)


def filter_and_score(
    jobs: list[JobPost],
    resume_text: str,
    threshold: float,
) -> list[tuple[JobPost, float]]:
    """Filter hard-skips, score remaining, return those >= threshold sorted desc."""
    results = []
    for job in jobs:
        if is_hard_skip(job):
            continue
        score = score_job(job, resume_text)
        if score >= threshold:
            results.append((job, score))
    return sorted(results, key=lambda x: x[1], reverse=True)
