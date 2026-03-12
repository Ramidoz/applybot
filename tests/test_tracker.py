import json
import pytest
from datetime import date
from applybot.tracker import (
    load_tracker, save_tracker, add_application,
    is_duplicate, update_status, make_app_id, TRACKER_SCHEMA_VERSION,
)


def test_load_tracker_returns_empty_on_missing(tmp_path):
    t = load_tracker(tmp_path / "applications_tracker.json")
    assert t["applications"] == []
    assert t["schema_version"] == TRACKER_SCHEMA_VERSION


def test_load_tracker_reads_existing(tmp_path):
    data = {"schema_version": "1.0", "applications": [{"id": "x"}]}
    (tmp_path / "applications_tracker.json").write_text(json.dumps(data))
    t = load_tracker(tmp_path / "applications_tracker.json")
    assert t["applications"][0]["id"] == "x"


def test_add_application_appends_record(empty_tracker):
    record = {
        "id": "acme-swe-2026-03-12",
        "company": "Acme",
        "role": "Software Engineer",
        "job_url": "https://acme.com/jobs/1",
        "platform": "greenhouse",
        "score": 82,
        "status": "dry_run",
        "ai_answered": False,
        "applied_date": None,
        "resume_path": "output/resumes/Acme_SWE_Resume.docx",
        "cover_letter_path": "output/cover_letters/Acme_SWE_CoverLetter.docx",
        "outreach_draft": None,
        "notes": "",
        "follow_up_dates": [],
    }
    result = add_application(empty_tracker, record)
    assert len(result["applications"]) == 1
    assert result["applications"][0]["company"] == "Acme"


def test_is_duplicate_true_within_30_days(empty_tracker):
    empty_tracker["applications"].append({
        "id": "acme-swe-2026-03-12",
        "company": "Acme",
        "job_url": "https://acme.com/jobs/1",
        "applied_date": "2026-03-01",
        "status": "submitted",
    })
    assert is_duplicate(empty_tracker, "https://acme.com/jobs/1", days=30) is True


def test_is_duplicate_false_if_expired_or_old(empty_tracker):
    empty_tracker["applications"].append({
        "id": "acme-swe-2025-01-01",
        "company": "Acme",
        "job_url": "https://acme.com/jobs/1",
        "applied_date": "2025-01-01",
        "status": "submitted",
    })
    assert is_duplicate(empty_tracker, "https://acme.com/jobs/1", days=30) is False


def test_update_status_changes_record(empty_tracker):
    empty_tracker["applications"].append({"id": "acme-swe-2026-03-12", "status": "dry_run"})
    result = update_status(empty_tracker, "acme-swe-2026-03-12", "submitted")
    assert result["applications"][0]["status"] == "submitted"


def test_save_and_reload_tracker(tmp_path, empty_tracker):
    path = tmp_path / "applications_tracker.json"
    save_tracker(empty_tracker, path)
    reloaded = load_tracker(path)
    assert reloaded["schema_version"] == TRACKER_SCHEMA_VERSION


def test_make_app_id_format():
    app_id = make_app_id("Acme Corp", "Senior Software Engineer", "2026-03-12")
    # Must be URL-safe (no spaces, special chars)
    assert " " not in app_id
    assert "acme" in app_id
    assert "2026-03-12" in app_id
    # Slash-containing roles should not break it
    app_id2 = make_app_id("X/Y Inc", "ML/AI Engineer", "2026-03-12")
    assert "/" not in app_id2
