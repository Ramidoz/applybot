"""Browser automation for form submission."""
from __future__ import annotations
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


def submit_application(job: JobPost, config: dict[str, Any], _page=None) -> str:
    """Returns status string. _page is injectable for testing (skips Playwright launch)."""
    raise NotImplementedError(
        "Browser automation not yet implemented. Run with --no-apply."
    )


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
                locator = page.locator(f"input[placeholder*='{label}' i], input[aria-label*='{label}' i]")
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
                label_id = ta.get_attribute("aria-labelledby") or ta.get_attribute("id") or ""
                if label_id:
                    label_el = page.locator(f"label[for='{label_id}'], #{label_id}")
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
