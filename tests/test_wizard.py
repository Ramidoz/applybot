import json
import pytest
from unittest.mock import patch
from applybot.wizard import run_wizard
from applybot.config import load_config


WIZARD_ANSWERS = [
    "Jane Smith",           # name
    "jane@example.com",     # email
    "555-000-0000",         # phone
    "linkedin.com/in/jane", # linkedin_url
    "",                     # portfolio_url (optional, skip)
    "Software Engineer, Backend Engineer",  # target_roles
    "y",                    # remote_only
    # location skipped (remote_only=True — wizard skips this step via continue)
    "BigCorp",              # blocklist_companies
    "100000",               # salary_min
    "160000",               # salary_max
    "4",                    # years_of_experience
    "y",                    # work_authorized
    "n",                    # require_sponsorship
    "resume.md",            # master_resume
    "n",                    # autofill
    "",                     # score_threshold (accept default 70)
    "none",                 # llm_provider
]


def test_wizard_produces_valid_config(tmp_path):
    """run_wizard with mocked prompt_toolkit inputs writes a valid applybot.json."""
    with patch("applybot.wizard.prompt", side_effect=WIZARD_ANSWERS):
        run_wizard(output_dir=tmp_path)

    cfg = load_config(tmp_path / "applybot.json")
    assert cfg["name"] == "Jane Smith"
    assert cfg["target_roles"] == ["Software Engineer", "Backend Engineer"]
    assert cfg["remote_only"] is True
    assert cfg["autofill"] is False
    assert cfg["score_threshold"] == 70
    assert cfg["llm_provider"] == "none"


def test_wizard_creates_gitignore(tmp_path):
    with patch("applybot.wizard.prompt", side_effect=WIZARD_ANSWERS):
        run_wizard(output_dir=tmp_path)
    gitignore = (tmp_path / ".gitignore").read_text()
    assert "applybot.json" in gitignore
    assert "sessions/" in gitignore


def test_wizard_creates_output_dirs(tmp_path):
    with patch("applybot.wizard.prompt", side_effect=WIZARD_ANSWERS):
        run_wizard(output_dir=tmp_path)
    assert (tmp_path / "output" / "resumes").is_dir()
    assert (tmp_path / "output" / "cover_letters").is_dir()
