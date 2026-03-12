import pytest
import responses as rsps_lib
from applybot.scraper import scrape_jobs, build_search_url, JobPost


def test_job_post_dataclass():
    job = JobPost(
        title="Software Engineer",
        company="Acme",
        url="https://acme.com/jobs/1",
        description="Python FastAPI PostgreSQL",
        platform="linkedin",
    )
    assert job.title == "Software Engineer"


def test_build_search_url_linkedin_remote():
    url = build_search_url("linkedin", "Software Engineer", remote_only=True, location="")
    assert "linkedin.com" in url
    assert "Software+Engineer" in url or "Software%20Engineer" in url


def test_build_search_url_indeed_with_location():
    url = build_search_url("indeed", "Nurse Practitioner", remote_only=False, location="New York, NY")
    assert "indeed.com" in url


@rsps_lib.activate
def test_scrape_jobs_deduplicates(sample_config, tmp_path):
    """scrape_jobs returns an empty list when all results are in the tracker."""
    from applybot.tracker import load_tracker
    tracker = load_tracker(tmp_path / "applications_tracker.json")
    # Pre-populate tracker with a URL
    tracker["applications"].append({
        "job_url": "https://linkedin.com/jobs/view/123",
        "status": "submitted",
        "applied_date": "2026-03-10",
    })

    # Mock LinkedIn search page — minimal HTML
    rsps_lib.add(
        rsps_lib.GET,
        "https://www.linkedin.com/jobs/search/",
        body="""
        <html><body>
        <a class="base-card__full-link" href="https://linkedin.com/jobs/view/123">SWE at Acme</a>
        </body></html>
        """,
        status=200,
    )

    results = scrape_jobs(sample_config, tracker, sources=["linkedin"])
    assert all(r.url != "https://linkedin.com/jobs/view/123" for r in results)
