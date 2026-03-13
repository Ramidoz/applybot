import json
import pytest
from pathlib import Path


SAMPLE_CONFIG = {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "555-000-0000",
    "linkedin_url": "https://linkedin.com/in/janesmith",
    "portfolio_url": "https://janesmith.dev",
    "target_roles": ["Software Engineer", "Backend Engineer"],
    "remote_only": True,
    "location": "",
    "blocklist_companies": ["BigCorp"],
    "salary_min": 100000,
    "salary_max": 160000,
    "years_of_experience": "4",
    "work_authorized": "Yes",
    "require_sponsorship": "No",
    "master_resume": "resume.md",
    "autofill": False,
    "score_threshold": 70,
    "llm_provider": "none",
    "llm_api_key": "",
    "llm_model": "",
    "llm_custom_url": "",
    "llm_custom_auth_header": "",
}

SAMPLE_RESUME_MD = """
# Jane Smith
Software Engineer | jane@example.com

## Skills
Python, FastAPI, PostgreSQL, Docker, Kubernetes, AWS, Redis

## Experience
### Senior Software Engineer - Acme Corp (2022-present)
- Built event-driven microservices in Python/FastAPI serving 5M req/day
- Reduced P99 latency by 40% via Redis caching layer

## Education
B.S. Computer Science, State University, 2020
"""


@pytest.fixture
def tmp_project(tmp_path):
    """A temporary project directory with config, resume, and output dirs."""
    config_path = tmp_path / "applybot.json"
    config = dict(SAMPLE_CONFIG)
    config["master_resume"] = str(tmp_path / "resume.md")
    config_path.write_text(json.dumps(config))

    resume_path = tmp_path / "resume.md"
    resume_path.write_text(SAMPLE_RESUME_MD)

    (tmp_path / "output" / "resumes").mkdir(parents=True)
    (tmp_path / "output" / "cover_letters").mkdir(parents=True)

    return tmp_path


@pytest.fixture
def sample_config(tmp_project):
    config = dict(SAMPLE_CONFIG)
    config["master_resume"] = str(tmp_project / "resume.md")
    return config


@pytest.fixture
def empty_tracker():
    return {"schema_version": "1.0", "applications": []}
