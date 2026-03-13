import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from applybot.pipeline import run_pipeline
from applybot.scraper import JobPost


MOCK_JOBS = [
    JobPost(
        title="Software Engineer",
        company="MockCo",
        url="https://mockco.com/jobs/1",
        description="Python FastAPI PostgreSQL Docker Kubernetes microservices REST API",
        platform="greenhouse",
    )
]


def test_dry_run_pipeline_writes_tracker(tmp_project, sample_config):
    """Full dry-run pipeline: scrape → score → generate → track → dashboard."""
    tracker_path = tmp_project / "applications_tracker.json"

    with patch("applybot.pipeline.scrape_jobs", return_value=MOCK_JOBS), \
         patch("applybot.pipeline.build_dashboard") as mock_dash, \
         patch("applybot.pipeline.open_dashboard"):

        run_pipeline(
            config=sample_config,
            dry_run=True,
            no_apply=True,
            project_dir=tmp_project,
        )

    assert tracker_path.exists()
    tracker = json.loads(tracker_path.read_text())
    assert len(tracker["applications"]) == 1
    app = tracker["applications"][0]
    assert app["company"] == "MockCo"
    assert app["status"] == "dry_run"
    assert app["score"] >= 70
    assert Path(app["resume_path"]).exists() or Path(tmp_project / app["resume_path"]).exists()

    mock_dash.assert_called_once()


def test_no_apply_pipeline_skips_apply(tmp_project, sample_config):
    with patch("applybot.pipeline.scrape_jobs", return_value=MOCK_JOBS), \
         patch("applybot.pipeline.submit_application") as mock_apply, \
         patch("applybot.pipeline.build_dashboard"), \
         patch("applybot.pipeline.open_dashboard"):

        run_pipeline(config=sample_config, dry_run=False, no_apply=True, project_dir=tmp_project)

    mock_apply.assert_not_called()


def test_below_threshold_jobs_skipped(tmp_project, sample_config):
    low_score_job = JobPost(
        title="Sales Director",
        company="SalesCo",
        url="https://salesCo.com/jobs/1",
        description="Sales quota B2B CRM account management pipeline forecasting",
        platform="indeed",
    )
    with patch("applybot.pipeline.scrape_jobs", return_value=[low_score_job]), \
         patch("applybot.pipeline.build_dashboard"), \
         patch("applybot.pipeline.open_dashboard"):

        run_pipeline(config=sample_config, dry_run=True, no_apply=True, project_dir=tmp_project)

    tracker_path = tmp_project / "applications_tracker.json"
    tracker = json.loads(tracker_path.read_text())
    assert len(tracker["applications"]) == 0
