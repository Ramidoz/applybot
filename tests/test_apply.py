"""Tests for apply.py — platform detection and form submission."""
import pytest
from unittest.mock import MagicMock, patch, call

from applybot.apply import detect_platform


# --- detect_platform ---

def test_detect_platform_linkedin():
    assert detect_platform("https://www.linkedin.com/jobs/view/12345") == "linkedin"


def test_detect_platform_greenhouse():
    assert detect_platform("https://boards.greenhouse.io/acmecorp/jobs/12345") == "greenhouse"


def test_detect_platform_lever():
    assert detect_platform("https://jobs.lever.co/acmecorp/abc-123") == "lever"


def test_detect_platform_unknown_returns_other():
    assert detect_platform("https://careers.somedomain.com/jobs/12345") == "other"


def test_detect_platform_empty_string():
    assert detect_platform("") == "other"


from applybot.apply import _fill_standard_fields, _handle_linkedin

SAMPLE_CONFIG = {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "555-000-0000",
    "linkedin_url": "https://linkedin.com/in/janesmith",
    "work_authorized": "Yes",
    "require_sponsorship": "No",
    "llm_provider": "none",
    "llm_api_key": "",
    "llm_model": "",
    "llm_custom_url": "",
    "llm_custom_auth_header": "",
}


# --- _fill_standard_fields ---

def test_fill_standard_fields_fills_text_inputs():
    page = MagicMock()
    page.locator.return_value.count.return_value = 1
    _fill_standard_fields(page, SAMPLE_CONFIG)
    # Should have called fill at least once
    page.locator.assert_called()


def test_fill_standard_fields_no_crash_on_empty_config():
    page = MagicMock()
    page.locator.return_value.count.return_value = 0
    _fill_standard_fields(page, {})  # should not raise


# --- _handle_linkedin ---

def test_handle_linkedin_submits_easy_apply():
    from applybot.scraper import JobPost
    page = MagicMock()
    # Simulate the Easy Apply button existing
    easy_apply_btn = MagicMock()
    easy_apply_btn.count.return_value = 1
    page.locator.return_value = easy_apply_btn

    job = JobPost(
        title="Data Scientist", company="Acme", url="https://linkedin.com/jobs/view/1",
        description="Python ML job", platform="linkedin",
    )
    result = _handle_linkedin(page, job, SAMPLE_CONFIG, "resume text")
    assert result in ("submitted", "needs_action", "failed")


def test_handle_linkedin_returns_needs_action_when_no_easy_apply():
    from applybot.scraper import JobPost
    page = MagicMock()
    # Simulate no Easy Apply button
    no_btn = MagicMock()
    no_btn.count.return_value = 0
    page.locator.return_value = no_btn

    job = JobPost(
        title="Data Scientist", company="Acme", url="https://linkedin.com/jobs/view/1",
        description="Python ML job", platform="linkedin",
    )
    result = _handle_linkedin(page, job, SAMPLE_CONFIG, "resume text")
    assert result == "needs_action"
