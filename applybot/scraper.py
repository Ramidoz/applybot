"""Scrape LinkedIn and Indeed for job postings."""
from __future__ import annotations
import re
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode, quote_plus

import requests
from bs4 import BeautifulSoup

from applybot.tracker import is_duplicate

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass
class JobPost:
    title: str
    company: str
    url: str
    description: str
    platform: str


def build_search_url(
    platform: str,
    role: str,
    remote_only: bool,
    location: str,
) -> str:
    if platform == "linkedin":
        params: dict[str, str] = {
            "keywords": role,
            "f_TPR": "r21600",  # last 6 hours
        }
        if remote_only:
            params["f_WT"] = "2"  # remote
        else:
            params["location"] = location
        return "https://www.linkedin.com/jobs/search/?" + urlencode(params)

    if platform == "indeed":
        params = {"q": role, "sort": "date"}
        if remote_only:
            params["remotejob"] = "032b3046-06a3-4876-8dfd-474eb5e7ed11"
        else:
            params["l"] = location
        return "https://www.indeed.com/jobs?" + urlencode(params)

    raise ValueError(f"Unknown platform: {platform}")


def _fetch(url: str, session: requests.Session) -> str | None:
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException:
        return None


def _parse_linkedin(html: str, base_url: str) -> list[JobPost]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    for card in soup.select("a.base-card__full-link")[:15]:
        href = card.get("href", "")
        title = card.get_text(strip=True)
        if href and title:
            jobs.append(JobPost(
                title=title,
                company="",
                url=href.split("?")[0],
                description="",
                platform="linkedin",
            ))
    return jobs


def _parse_indeed(html: str) -> list[JobPost]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    for card in soup.select("a.jcs-JobTitle")[:10]:
        href = card.get("href", "")
        title = card.get_text(strip=True)
        if href:
            full_url = "https://www.indeed.com" + href if href.startswith("/") else href
            jobs.append(JobPost(
                title=title,
                company="",
                url=full_url.split("&")[0],
                description="",
                platform="indeed",
            ))
    return jobs


def scrape_jobs(
    config: dict[str, Any],
    tracker: dict[str, Any],
    sources: list[str] | None = None,
) -> list[JobPost]:
    """Scrape jobs for all target_roles. Deduplicates against tracker."""
    if sources is None:
        sources = ["linkedin", "indeed"]

    blocklist = {c.lower() for c in config.get("blocklist_companies", [])}
    session = requests.Session()
    all_jobs: list[JobPost] = []
    seen_urls: set[str] = set()

    for role in config["target_roles"]:
        for platform in sources:
            url = build_search_url(
                platform, role,
                remote_only=config.get("remote_only", True),
                location=config.get("location", ""),
            )
            html = _fetch(url, session)
            if not html:
                continue

            if platform == "linkedin":
                jobs = _parse_linkedin(html, url)
            else:
                jobs = _parse_indeed(html)

            for job in jobs:
                if job.url in seen_urls:
                    continue
                if is_duplicate(tracker, job.url):
                    continue
                if job.company.lower() in blocklist:
                    continue
                seen_urls.add(job.url)
                all_jobs.append(job)

            time.sleep(1)  # polite delay between requests

    return all_jobs
