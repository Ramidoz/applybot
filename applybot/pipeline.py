"""Orchestrate the full applybot pipeline."""
from __future__ import annotations
from datetime import date, datetime
from pathlib import Path
from typing import Any

from rich.console import Console

from applybot.scraper import scrape_jobs, JobPost
from applybot.scorer import filter_and_score
from applybot.generator import generate_resume, generate_cover_letter
from applybot.tracker import load_tracker, save_tracker, add_application, make_app_id
from applybot.dashboard import build_dashboard, open_dashboard

console = Console()


def submit_application(job: JobPost, config: dict[str, Any], resume_text: str = "") -> str:
    """Wrapper — imports apply lazily to avoid requiring playwright for --no-apply mode."""
    from applybot.apply import submit_application as _submit
    return _submit(job, config, resume_text=resume_text)


def run_pipeline(
    config: dict[str, Any],
    dry_run: bool = False,
    no_apply: bool = False,
    project_dir: Path | None = None,
) -> None:
    project_dir = Path(project_dir or Path.cwd())
    tracker_path = project_dir / "applications_tracker.json"
    output_dir = project_dir / "output"

    tracker = load_tracker(tracker_path)
    resume_path = Path(config["master_resume"])
    if not resume_path.is_absolute():
        resume_path = project_dir / resume_path
    resume_text = resume_path.read_text(encoding="utf-8") if resume_path.exists() else ""

    # Stage 1: Scrape
    console.rule("[bold purple][1/5] Scraping job boards[/bold purple]")
    raw_jobs = scrape_jobs(config, tracker)
    console.print(f"  Found [green]{len(raw_jobs)}[/green] new job(s)")

    # Stage 2: Score + filter
    console.rule("[bold purple][2/5] Scoring jobs[/bold purple]")
    scored = filter_and_score(raw_jobs, resume_text, threshold=config["score_threshold"])
    console.print(f"  [green]{len(scored)}[/green] job(s) passed threshold (≥{config['score_threshold']})")

    # Stage 3: Generate docs + Stage 4: Apply
    console.rule("[bold purple][3/5] Generating documents[/bold purple]")
    for job, score in scored:
        resume_out = generate_resume(
            job=job, resume_text=resume_text, config=config,
            output_dir=output_dir / "resumes",
        )
        cl_out = generate_cover_letter(
            job=job, resume_text=resume_text, config=config,
            output_dir=output_dir / "cover_letters",
        )
        console.print(f"  [dim]→ {job.company} — {job.title}[/dim]")

        # Determine status
        status = "dry_run"
        if not dry_run and not no_apply and config.get("autofill"):
            console.rule("[bold purple][4/5] Submitting applications[/bold purple]")
            try:
                status = submit_application(job, config, resume_text=resume_text)
            except Exception as exc:
                status = "failed"
                console.print(f"[red]  Application failed: {exc}[/red]")
        elif not dry_run and not no_apply:
            status = "needs_action"

        # Convert relative paths for tracker storage
        try:
            resume_rel = str(resume_out.relative_to(project_dir))
        except ValueError:
            # Different drives on Windows
            resume_rel = str(resume_out)

        try:
            cl_rel = str(cl_out.relative_to(project_dir))
        except ValueError:
            # Different drives on Windows
            cl_rel = str(cl_out)

        app_id = make_app_id(job.company, job.title)
        record = {
            "id": app_id,
            "company": job.company,
            "role": job.title,
            "job_url": job.url,
            "platform": job.platform,
            "score": score,
            "status": status,
            "ai_answered": False,
            "applied_date": date.today().isoformat() if status == "submitted" else None,
            "resume_path": resume_rel,
            "cover_letter_path": cl_rel,
            "outreach_draft": None,
            "notes": "",
            "follow_up_dates": [],
        }
        tracker = add_application(tracker, record)

    # Stage 5: Save + dashboard
    tracker["last_run"] = datetime.now().isoformat(timespec="seconds")
    save_tracker(tracker, tracker_path)

    console.rule("[bold purple][5/5] Building dashboard[/bold purple]")
    dash_path = build_dashboard(tracker, output_dir=output_dir)
    console.print(f"  Dashboard → [cyan]{dash_path}[/cyan]")
    open_dashboard(dash_path)

    submitted = sum(1 for a in tracker["applications"] if a["status"] == "submitted")
    action = sum(1 for a in tracker["applications"] if a["status"] in ("needs_action", "captcha"))
    console.print(
        f"\n[bold green]Run complete.[/bold green] "
        f"{submitted} submitted · {action} needs action"
    )
