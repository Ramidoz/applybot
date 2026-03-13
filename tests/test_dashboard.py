import json
import pytest
from pathlib import Path
from applybot.dashboard import build_dashboard


SAMPLE_TRACKER = {
    "schema_version": "1.0",
    "last_run": "2026-03-12T10:00:00",
    "applications": [
        {
            "id": "acme-swe-2026-03-12",
            "company": "Acme",
            "role": "Software Engineer",
            "job_url": "https://acme.com/jobs/1",
            "platform": "greenhouse",
            "score": 85,
            "status": "submitted",
            "ai_answered": False,
            "applied_date": "2026-03-12",
            "resume_path": "file:///D:/Work/applybot/output/resumes/Acme_SWE_Resume.docx",
            "cover_letter_path": "file:///D:/Work/applybot/output/cover_letters/Acme_SWE_CL.docx",
            "outreach_draft": None,
            "notes": "",
            "follow_up_dates": ["2026-03-17"],
        }
    ],
}


def test_build_dashboard_creates_html(tmp_path):
    out = build_dashboard(SAMPLE_TRACKER, output_dir=tmp_path)
    assert out.exists()
    assert out.suffix == ".html"


def test_build_dashboard_injects_data(tmp_path):
    build_dashboard(SAMPLE_TRACKER, output_dir=tmp_path)
    html = (tmp_path / "dashboard.html").read_text(encoding="utf-8")
    assert "Acme" in html
    assert "submitted" in html
    assert "2026-03-12" in html


def test_build_dashboard_has_no_placeholder_token(tmp_path):
    build_dashboard(SAMPLE_TRACKER, output_dir=tmp_path)
    html = (tmp_path / "dashboard.html").read_text(encoding="utf-8")
    assert "__APPLYBOT_DATA__" not in html


def test_build_dashboard_file_path_in_html(tmp_path):
    build_dashboard(SAMPLE_TRACKER, output_dir=tmp_path)
    html = (tmp_path / "dashboard.html").read_text(encoding="utf-8")
    assert "file:///" in html
