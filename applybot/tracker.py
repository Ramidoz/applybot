"""Read/write applications_tracker.json."""
from __future__ import annotations
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

TRACKER_SCHEMA_VERSION = "1.0"
VALID_STATUSES = {
    "dry_run", "submitted", "needs_action",
    "captcha", "ai_answered", "failed", "expired",
}


def _empty_tracker() -> dict[str, Any]:
    return {"schema_version": TRACKER_SCHEMA_VERSION, "applications": []}


def load_tracker(path: Path) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return _empty_tracker()
    return json.loads(path.read_text(encoding="utf-8"))


def save_tracker(tracker: dict[str, Any], path: Path) -> None:
    Path(path).write_text(
        json.dumps(tracker, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def add_application(tracker: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    tracker["applications"].append(record)
    return tracker


def is_duplicate(tracker: dict[str, Any], job_url: str, days: int = 30) -> bool:
    """Return True if this URL was applied to within `days` days and is not expired."""
    cutoff = date.today() - timedelta(days=days)
    for app in tracker["applications"]:
        if app.get("job_url") != job_url:
            continue
        if app.get("status") == "expired":
            continue
        applied = app.get("applied_date")
        if applied and datetime.strptime(applied, "%Y-%m-%d").date() >= cutoff:
            return True
    return False


def update_status(
    tracker: dict[str, Any], app_id: str, status: str
) -> dict[str, Any]:
    for app in tracker["applications"]:
        if app.get("id") == app_id:
            app["status"] = status
    return tracker


def make_app_id(company: str, role: str, applied_date: str | None = None) -> str:
    today = applied_date or date.today().isoformat()
    slug = lambda s: s.lower().replace(" ", "-").replace("/", "-")[:20]
    return f"{slug(company)}-{slug(role)}-{today}"
