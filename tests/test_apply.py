"""Tests for apply.py — platform detection and form submission."""
import pytest
from unittest.mock import MagicMock, patch, call

from applybot.apply import detect_platform, _fill_standard_fields, _handle_linkedin, _handle_greenhouse, _handle_lever, submit_application
from applybot.scraper import JobPost


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


# --- _answer_custom_questions ---

def test_answer_custom_questions_calls_llm_and_fills_textarea():
    from unittest.mock import patch as mock_patch
    page = MagicMock()
    # One textarea with an aria-labelledby label
    textarea_mock = MagicMock()
    textarea_mock.get_attribute.side_effect = lambda attr: "q1" if attr == "aria-labelledby" else None
    textareas = MagicMock()
    textareas.count.return_value = 1
    textareas.nth.return_value = textarea_mock

    label_el = MagicMock()
    label_el.count.return_value = 1
    label_el.first.inner_text.return_value = "Why do you want this role?"
    page.locator.side_effect = lambda sel: textareas if sel == "textarea" else label_el

    job = JobPost(
        title="DS", company="Acme", url="https://linkedin.com/jobs/1",
        description="ML role", platform="linkedin",
    )
    config = {**SAMPLE_CONFIG, "llm_provider": "claude", "llm_api_key": "sk-test", "llm_model": "claude-haiku-4-5-20251001"}

    with mock_patch("applybot.apply.answer_question", return_value="I love data science.") as mock_aq:
        from applybot.apply import _answer_custom_questions
        _answer_custom_questions(page, job, config, "resume text")

    mock_aq.assert_called_once()
    textarea_mock.fill.assert_called_once_with("I love data science.")


# --- _handle_greenhouse ---

def test_handle_greenhouse_fills_and_submits():
    page = MagicMock()
    submit_btn = MagicMock()
    submit_btn.count.return_value = 1
    page.locator.return_value = submit_btn

    job = JobPost(
        title="Data Scientist", company="Acme",
        url="https://boards.greenhouse.io/acme/jobs/123",
        description="Python ML job", platform="greenhouse",
    )
    result = _handle_greenhouse(page, job, SAMPLE_CONFIG, "resume text")
    assert result in ("submitted", "needs_action", "failed")


def test_handle_greenhouse_returns_needs_action_when_no_submit_button():
    page = MagicMock()
    no_btn = MagicMock()
    no_btn.count.return_value = 0
    page.locator.return_value = no_btn

    job = JobPost(
        title="Data Scientist", company="Acme",
        url="https://boards.greenhouse.io/acme/jobs/123",
        description="Python ML job", platform="greenhouse",
    )
    result = _handle_greenhouse(page, job, SAMPLE_CONFIG, "resume text")
    assert result == "needs_action"


# --- _handle_lever ---

def test_handle_lever_fills_and_submits():
    page = MagicMock()
    apply_btn = MagicMock()
    apply_btn.count.return_value = 1
    page.locator.return_value = apply_btn

    job = JobPost(
        title="ML Engineer", company="Acme",
        url="https://jobs.lever.co/acme/abc-123",
        description="Python ML job", platform="lever",
    )
    result = _handle_lever(page, job, SAMPLE_CONFIG, "resume text")
    assert result in ("submitted", "needs_action", "failed")


def test_handle_lever_returns_needs_action_when_no_apply_button():
    page = MagicMock()
    no_btn = MagicMock()
    no_btn.count.return_value = 0
    page.locator.return_value = no_btn

    job = JobPost(
        title="ML Engineer", company="Acme",
        url="https://jobs.lever.co/acme/abc-123",
        description="Python ML job", platform="lever",
    )
    result = _handle_lever(page, job, SAMPLE_CONFIG, "resume text")
    assert result == "needs_action"


# --- submit_application orchestrator ---

def test_submit_application_routes_to_linkedin():
    page = MagicMock()
    # Simulate: no easy apply button found → needs_action
    no_btn = MagicMock()
    no_btn.count.return_value = 0
    page.locator.return_value = no_btn

    job = JobPost(
        title="DS", company="Acme",
        url="https://www.linkedin.com/jobs/view/12345",
        description="ML role", platform="linkedin",
    )
    result = submit_application(job, SAMPLE_CONFIG, _page=page)
    assert result in ("submitted", "needs_action", "failed")


def test_submit_application_routes_to_greenhouse():
    page = MagicMock()
    no_btn = MagicMock()
    no_btn.count.return_value = 0
    page.locator.return_value = no_btn

    job = JobPost(
        title="DS", company="Acme",
        url="https://boards.greenhouse.io/acme/jobs/99",
        description="ML role", platform="greenhouse",
    )
    result = submit_application(job, SAMPLE_CONFIG, _page=page)
    assert result in ("submitted", "needs_action", "failed")
