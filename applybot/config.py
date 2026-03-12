"""Load, save, and validate applybot.json configuration."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any


REQUIRED_KEYS = [
    "name", "email", "phone", "linkedin_url", "target_roles",
    "remote_only", "location", "salary_min", "salary_max",
    "years_of_experience", "work_authorized", "require_sponsorship",
    "master_resume", "autofill", "score_threshold", "llm_provider",
    "llm_api_key", "llm_model", "llm_custom_url", "llm_custom_auth_header",
]

DEFAULTS = {
    "portfolio_url": "",
    "blocklist_companies": [],
    "location": "",
    "llm_api_key": "",
    "llm_model": "",
    "llm_custom_url": "",
    "llm_custom_auth_header": "",
}


class ConfigError(Exception):
    pass


def load_config(path: Path) -> dict[str, Any]:
    """Load and validate applybot.json. Raises ConfigError on failure."""
    path = Path(path)
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ConfigError(f"Config file contains invalid JSON: {e}") from e
    # Apply defaults for optional fields
    for k, v in DEFAULTS.items():
        data.setdefault(k, v)
    validate_config(data)
    return data


def save_config(config: dict[str, Any], path: Path) -> None:
    """Write config dict to applybot.json."""
    Path(path).write_text(
        json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def validate_config(config: dict[str, Any]) -> None:
    """Raise ConfigError if config is missing required fields or has bad values."""
    for key in REQUIRED_KEYS:
        if key not in config:
            raise ConfigError(f"Missing required config field: {key}")

    if not isinstance(config["target_roles"], list) or len(config["target_roles"]) == 0:
        raise ConfigError("target_roles must be a non-empty list of job title strings")

    threshold = config["score_threshold"]
    if not isinstance(threshold, (int, float)) or not (0 <= threshold <= 100):
        raise ConfigError(f"score_threshold must be a number between 0 and 100, got: {threshold}")

    valid_providers = {"claude", "openai", "custom", "none"}
    if config["llm_provider"] not in valid_providers:
        raise ConfigError(f"llm_provider must be one of {valid_providers}")
