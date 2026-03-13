"""Browser automation for form submission."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from applybot.scraper import JobPost
from applybot.contextual import answer_question


def detect_platform(url: str) -> str:
    """Return platform name from job URL: linkedin | greenhouse | lever | other."""
    if "linkedin.com" in url:
        return "linkedin"
    if "greenhouse.io" in url:
        return "greenhouse"
    if "lever.co" in url:
        return "lever"
    return "other"


# Maps config keys to common form field label patterns
_FIELD_MAP = {
    "email": ["email", "e-mail"],
    "phone": ["phone", "mobile", "telephone"],
    "name": ["full name", "your name", "first and last name"],
    "linkedin_url": ["linkedin", "linkedin url", "linkedin profile"],
}


def _fill_standard_fields(page: Any, config: dict[str, Any]) -> None:
    """Fill common form fields (email, phone, name) from config."""
    for config_key, labels in _FIELD_MAP.items():
        value = config.get(config_key, "")
        if not value:
            continue
        for label in labels:
            try:
                safe_label = label.replace("'", "\\'")
                locator = page.locator(f"input[placeholder*='{safe_label}' i], input[aria-label*='{safe_label}' i]")
                if locator.count() > 0:
                    locator.first.fill(value)
                    break
            except Exception:
                pass


def _answer_custom_questions(page: Any, job: JobPost, config: dict[str, Any], resume_text: str) -> None:
    """Detect open-text textareas not in standard field map and fill via LLM."""
    if config.get("llm_provider", "none") == "none":
        return
    try:
        textareas = page.locator("textarea")
        count = textareas.count()
        for i in range(count):
            ta = textareas.nth(i)
            label_text = ""
            try:
                labelledby_id = ta.get_attribute("aria-labelledby") or ""
                own_id = ta.get_attribute("id") or ""
                if labelledby_id:
                    label_el = page.locator(f"#{labelledby_id}")
                    if label_el.count() > 0:
                        label_text = label_el.first.inner_text()
                elif own_id:
                    label_el = page.locator(f"label[for='{own_id}']")
                    if label_el.count() > 0:
                        label_text = label_el.first.inner_text()
            except Exception:
                pass
            if label_text:
                answer = answer_question(label_text, job.description, resume_text, config)
                if answer:
                    ta.fill(answer)
    except Exception:
        pass


def _handle_linkedin(page: Any, job: JobPost, config: dict[str, Any], resume_text: str) -> str:
    """Handle LinkedIn Easy Apply flow. Returns status string."""
    try:
        page.goto(job.url, wait_until="domcontentloaded", timeout=15000)

        easy_apply = page.locator("button:has-text('Easy Apply'), button[aria-label*='Easy Apply' i]")
        if easy_apply.count() == 0:
            return "needs_action"

        easy_apply.first.click()
        page.wait_for_timeout(1000)

        _fill_standard_fields(page, config)

        # Answer any open-text custom questions
        _answer_custom_questions(page, job, config, resume_text)

        # Submit
        submit_btn = page.locator("button[aria-label*='Submit application' i], button:has-text('Submit application')")
        if submit_btn.count() > 0:
            submit_btn.first.click()
            page.wait_for_timeout(2000)
            return "submitted"

        return "needs_action"
    except Exception:
        return "failed"


def _handle_greenhouse(page: Any, job: JobPost, config: dict[str, Any], resume_text: str) -> str:
    """Handle Greenhouse application form. Returns status string."""
    try:
        page.goto(job.url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(1000)

        _fill_standard_fields(page, config)
        _answer_custom_questions(page, job, config, resume_text)

        submit_btn = page.locator(
            "button[type='submit'], input[type='submit'], button:has-text('Submit')"
        )
        if submit_btn.count() > 0:
            submit_btn.first.click()
            page.wait_for_timeout(2000)
            return "submitted"

        return "needs_action"
    except Exception:
        return "failed"


def _handle_lever(page: Any, job: JobPost, config: dict[str, Any], resume_text: str) -> str:
    """Handle Lever application form. Returns status string."""
    try:
        page.goto(job.url, wait_until="domcontentloaded", timeout=15000)

        apply_btn = page.locator(
            "a:has-text('Apply'), button:has-text('Apply'), a[href*='apply']"
        )
        if apply_btn.count() == 0:
            return "needs_action"

        apply_btn.first.click()
        page.wait_for_timeout(1000)

        _fill_standard_fields(page, config)
        _answer_custom_questions(page, job, config, resume_text)

        submit_btn = page.locator(
            "button:has-text('Submit application'), button[type='submit'], input[type='submit']"
        )
        if submit_btn.count() > 0:
            submit_btn.first.click()
            page.wait_for_timeout(2000)
            return "submitted"

        return "needs_action"
    except Exception:
        return "failed"


def submit_application(job: JobPost, config: dict[str, Any], resume_text: str = "", _page=None) -> str:
    """Submit a job application. Returns status string.

    _page: injectable Playwright page for testing (skips browser launch when provided).
    """
    platform = detect_platform(job.url)

    if _page is not None:
        # Testing path — use the provided page directly
        return _dispatch(platform, _page, job, config, resume_text)

    # Production path — launch Playwright
    from playwright.sync_api import sync_playwright  # lazy import
    cookies_path = Path("sessions") / "linkedin_cookies.json"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context()

        # Load saved cookies if available
        if cookies_path.exists():
            import json
            cookies = json.loads(cookies_path.read_text(encoding="utf-8"))
            context.add_cookies(cookies)

        page = context.new_page()
        try:
            result = _dispatch(platform, page, job, config, resume_text)
        finally:
            context.close()
            browser.close()

    return result


def _dispatch(platform: str, page: Any, job: JobPost, config: dict[str, Any], resume_text: str = "") -> str:
    """Route to the correct platform handler."""
    if platform == "linkedin":
        return _handle_linkedin(page, job, config, resume_text)
    elif platform == "greenhouse":
        return _handle_greenhouse(page, job, config, resume_text)
    elif platform == "lever":
        return _handle_lever(page, job, config, resume_text)
    else:
        return "needs_action"
