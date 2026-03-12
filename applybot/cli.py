"""Click entry point for all applybot commands."""
import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option()
def cli():
    """ApplyBot - automate your job search pipeline."""


@cli.command()
@click.option("--dir", "project_dir", default=".", show_default=True,
              help="Directory to write applybot.json into.")
def init(project_dir):
    """Interactive setup wizard — creates applybot.json."""
    from pathlib import Path
    from applybot.wizard import run_wizard
    run_wizard(output_dir=Path(project_dir))


@cli.command()
@click.argument("platform", type=click.Choice(["linkedin"]))
def login(platform):
    """Save session cookies for a platform (one-time login)."""
    if platform == "linkedin":
        console.print("[yellow]Opening Chrome for LinkedIn login...[/yellow]")
        console.print("[dim]Browser automation not yet implemented (Plan 2).[/dim]")


@cli.command()
@click.option("--dry-run", "dry_run", is_flag=True, default=False,
              help="Run pipeline without submitting any applications.")
@click.option("--no-apply", "no_apply", is_flag=True, default=False,
              help="Scraper-only mode: scrape, score, generate - no form submission.")
@click.option("--config", "config_path", default="applybot.json", show_default=True)
def run(dry_run, no_apply, config_path):
    """Full pipeline: scrape, score, generate, apply, dashboard."""
    from pathlib import Path
    from applybot.config import load_config
    from applybot.pipeline import run_pipeline

    cfg = load_config(Path(config_path))
    run_pipeline(cfg, dry_run=dry_run, no_apply=no_apply)


@cli.command()
@click.option("--config", "config_path", default="applybot.json", show_default=True)
def status(config_path):
    """Print ASCII status table of all applications."""
    from pathlib import Path
    from applybot.tracker import load_tracker
    from rich.table import Table

    tracker = load_tracker(Path("applications_tracker.json"))
    apps = tracker["applications"]

    table = Table(title="ApplyBot Status", show_lines=True)
    table.add_column("Company", style="bold")
    table.add_column("Role")
    table.add_column("Status")
    table.add_column("Score")
    table.add_column("Applied")

    STATUS_LABELS = {
        "submitted": "✅ Applied!",
        "needs_action": "👋 Needs Your Help",
        "captcha": "🤖 CAPTCHA Blocked",
        "ai_answered": "🤖 AI Filled",
        "failed": "❌ Failed",
        "expired": "💨 Expired",
        "dry_run": "🧪 Test Run",
    }

    for app in sorted(apps, key=lambda a: a.get("applied_date") or "", reverse=True):
        table.add_row(
            app.get("company", ""),
            app.get("role", ""),
            STATUS_LABELS.get(app.get("status", ""), app.get("status", "")),
            str(app.get("score", "")),
            app.get("applied_date") or "—",
        )

    console.print(table if apps else "[dim]No applications yet. Run 'applybot run' to get started.[/dim]")


@cli.command()
@click.option("--config", "config_path", default="applybot.json", show_default=True)
def dashboard(config_path):
    """Rebuild dashboard HTML and open in browser."""
    from pathlib import Path
    from applybot.config import load_config
    from applybot.tracker import load_tracker
    from applybot.dashboard import build_dashboard, open_dashboard

    cfg = load_config(Path(config_path))
    tracker = load_tracker(Path("applications_tracker.json"))
    out_path = build_dashboard(tracker, output_dir=Path("output"))
    open_dashboard(out_path)
