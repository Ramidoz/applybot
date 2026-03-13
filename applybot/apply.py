"""Browser automation for form submission. Implemented in Plan 2."""
from typing import Any
from applybot.scraper import JobPost


def submit_application(job: JobPost, config: dict[str, Any]) -> str:
    """Returns status string. Stub: always raises NotImplementedError."""
    raise NotImplementedError(
        "Browser automation not yet implemented. Run with --no-apply."
    )
