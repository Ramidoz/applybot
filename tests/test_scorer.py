import pytest
from applybot.scorer import score_job, extract_keywords, is_hard_skip
from applybot.scraper import JobPost


RESUME_TEXT = """
Python FastAPI PostgreSQL Docker Kubernetes AWS Redis
Senior Software Engineer microservices event-driven
4 years experience data pipelines REST API
"""

GOOD_JD = """
We're looking for a Senior Software Engineer with Python experience.
You'll build microservices using FastAPI and PostgreSQL.
Docker and Kubernetes experience preferred.
Remote friendly. Salary $130k–$160k.
"""

WEAK_JD = """
Sales Manager needed to lead a team of account executives.
5+ years B2B sales experience. CRM proficiency required.
"""

HARD_SKIP_JD = """
Must be US citizen or permanent resident. No visa sponsorship now or ever.
Senior Data Analyst role.
"""


def test_extract_keywords_returns_lowercase_tokens():
    kws = extract_keywords("Python FastAPI PostgreSQL 4 years REST")
    assert "python" in kws
    assert "fastapi" in kws
    # short words and numbers filtered
    assert "4" not in kws


def test_score_job_high_for_matching_jd():
    job = JobPost("Senior SWE", "Acme", "https://acme.com/1", GOOD_JD, "linkedin")
    score = score_job(job, RESUME_TEXT)
    assert score >= 70


def test_score_job_low_for_unrelated_jd():
    job = JobPost("Sales Manager", "Acme", "https://acme.com/2", WEAK_JD, "linkedin")
    score = score_job(job, RESUME_TEXT)
    assert score < 40


def test_is_hard_skip_us_citizen_only():
    job = JobPost("Data Analyst", "Corp", "https://corp.com/3", HARD_SKIP_JD, "indeed")
    assert is_hard_skip(job) is True


def test_is_hard_skip_normal_jd():
    job = JobPost("SWE", "Acme", "https://acme.com/4", GOOD_JD, "linkedin")
    assert is_hard_skip(job) is False


def test_score_returns_0_to_100():
    job = JobPost("SWE", "X", "https://x.com/1", GOOD_JD, "linkedin")
    score = score_job(job, RESUME_TEXT)
    assert 0 <= score <= 100
