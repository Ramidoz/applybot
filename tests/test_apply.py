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
