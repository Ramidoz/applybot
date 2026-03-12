"""Interactive setup wizard using prompt_toolkit."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from prompt_toolkit import prompt as _prompt
from rich.console import Console
from rich.panel import Panel

from applybot.config import save_config, validate_config

console = Console()


def prompt(message: str, default: str = "") -> str:
    """Thin wrapper so tests can mock it."""
    return _prompt(message) or default


STEPS = [
    # (field_key, display_name, explanation, default, required)
    ("name",           "Your full name",            "We'll put this on every resume and cover letter.", "", True),
    ("email",          "Email address",              "Your primary contact email.", "", True),
    ("phone",          "Phone number",               "Will appear on your resume.", "", True),
    ("linkedin_url",   "LinkedIn URL",               "e.g. linkedin.com/in/yourname", "", True),
    ("portfolio_url",  "Portfolio URL",              "Optional — press Enter to skip.", "", False),
    ("target_roles",   "Job titles to search for",  "Comma-separated. e.g. 'Software Engineer, Backend Engineer'", "", True),
    ("remote_only",    "Remote jobs only? (y/n)",   "Filter search results to remote positions.", "y", True),
    ("location",       "City or region",             "Only used if you chose non-remote. e.g. 'New York, NY'", "", False),
    ("blocklist_companies", "Companies to skip",     "Comma-separated. Press Enter to skip.", "", False),
    ("salary_min",     "Minimum salary",             "Numeric, no commas. e.g. 100000", "0", True),
    ("salary_max",     "Maximum salary",             "Numeric, no commas. e.g. 160000", "0", True),
    ("years_of_experience", "Years of experience",  "e.g. 4", "", True),
    ("work_authorized","Work authorized in the US? (y/n)", "Are you legally allowed to work without sponsorship right now?", "y", True),
    ("require_sponsorship", "Require sponsorship? (y/n)", "Will you need visa sponsorship now or in the future?", "n", True),
    ("master_resume",  "Path to your master resume","Your base .md or .docx resume file. e.g. resume.md", "resume.md", True),
    ("autofill",       "Auto-submit applications? (y/n)", "Full-auto mode submits forms automatically. 'n' = generate docs only.", "n", True),
    ("score_threshold","Match score threshold",      "Jobs scoring below this (0–100) are skipped. Press Enter for default.", "70", True),
    ("llm_provider",   "LLM provider",               "claude / openai / custom / none. Press Enter for none.", "none", True),
]

LLM_EXTRA_STEPS = [
    ("llm_api_key",           "API key",              "Your API key for the provider.", "", True),
    ("llm_model",             "Model name",           "e.g. claude-3-haiku-20240307", "", True),
]

CUSTOM_LLM_EXTRA = [
    ("llm_custom_url",        "Custom LLM base URL",  "e.g. http://localhost:11434/v1", "", True),
    ("llm_custom_auth_header","Auth header",          "e.g. Authorization: Bearer sk-...", "", True),
]


def run_wizard(output_dir: Path | None = None) -> dict[str, Any]:
    output_dir = Path(output_dir or Path.cwd())
    console.print(Panel("👋  [bold purple]ApplyBot Setup[/bold purple] — let's get you hired!", expand=False))

    total = len(STEPS)
    config: dict[str, Any] = {}

    for i, (key, label, explanation, default, required) in enumerate(STEPS, 1):
        console.print(f"\n[dim]Step {i} of {total}[/dim]")
        console.print(f"[cyan]{explanation}[/cyan]")
        prompt_text = f"  {label}"
        if default:
            prompt_text += f" [{default}]"
        prompt_text += ": "

        # Skip location if remote_only
        if key == "location" and config.get("remote_only") is True:
            config["location"] = ""
            continue

        raw = prompt(prompt_text, default)

        # Type coercions
        if key == "target_roles":
            config[key] = [r.strip() for r in raw.split(",") if r.strip()]
        elif key == "blocklist_companies":
            config[key] = [c.strip() for c in raw.split(",") if c.strip()] if raw else []
        elif key in ("remote_only", "work_authorized", "require_sponsorship", "autofill"):
            config[key] = raw.lower().startswith("y")
        elif key in ("salary_min", "salary_max"):
            config[key] = int(raw) if raw else 0
        elif key == "score_threshold":
            config[key] = float(raw) if raw else 70
        else:
            config[key] = raw

    # Extra LLM fields
    if config.get("llm_provider") != "none":
        for key, label, explanation, default, required in LLM_EXTRA_STEPS:
            console.print(f"\n[cyan]{explanation}[/cyan]")
            config[key] = prompt(f"  {label}: ", default)
        if config.get("llm_provider") == "custom":
            for key, label, explanation, default, required in CUSTOM_LLM_EXTRA:
                config[key] = prompt(f"  {label}: ", default)
    else:
        config["llm_api_key"] = ""
        config["llm_model"] = ""
        config["llm_custom_url"] = ""
        config["llm_custom_auth_header"] = ""

    validate_config(config)
    save_config(config, output_dir / "applybot.json")

    # .gitignore
    gitignore_path = output_dir / ".gitignore"
    existing = gitignore_path.read_text() if gitignore_path.exists() else ""
    additions = [e for e in ["applybot.json", "sessions/"] if e not in existing]
    if additions:
        with open(gitignore_path, "a") as f:
            f.write("\n" + "\n".join(additions) + "\n")

    # Output dirs
    (output_dir / "output" / "resumes").mkdir(parents=True, exist_ok=True)
    (output_dir / "output" / "cover_letters").mkdir(parents=True, exist_ok=True)

    console.print("\n[green bold]✓ Config saved → applybot.json[/green bold]")
    console.print("[yellow]⚠  applybot.json contains your API key — do not commit it to git[/yellow]")
    console.print("\nNext: run [bold]applybot run --dry-run[/bold] to test everything.")

    return config
