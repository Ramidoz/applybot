"""Browser automation for form submission."""
from __future__ import annotations
from typing import Any

from applybot.scraper import JobPost


def detect_platform(url: str) -> str:
    """Return platform name from job URL: linkedin | greenhouse | lever | other."""
    if "linkedin.com" in url:
        return "linkedin"
    if "greenhouse.io" in url:
        return "greenhouse"
    if "lever.co" in url:
        return "lever"
    return "other"


def submit_application(job: JobPost, config: dict[str, Any], _page=None) -> str:
    """Returns status string. _page is injectable for testing (skips Playwright launch)."""
    raise NotImplementedError(
        "Browser automation not yet implemented. Run with --no-apply."
    )
