"""Build output/dashboard.html with tracker data baked in. Open in browser."""
from __future__ import annotations
import json
import re
import webbrowser
from pathlib import Path
from typing import Any


TEMPLATE_PATH = Path(__file__).parent / "templates" / "dashboard.html"
PLACEHOLDER = "/*__APPLYBOT_DATA__*/"
END_PLACEHOLDER = "/*__END__*/"


def build_dashboard(
    tracker: dict[str, Any],
    output_dir: Path,
) -> Path:
    """Inject tracker JSON into dashboard template. Returns path to built file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    data_json = json.dumps(tracker, ensure_ascii=False)

    # Replace the placeholder block: /*__APPLYBOT_DATA__*/ {...} /*__END__*/
    # with just the data (no placeholder markers in output)
    pattern = re.escape(PLACEHOLDER) + r".*?" + re.escape(END_PLACEHOLDER)
    replacement = data_json
    built = re.sub(pattern, replacement, template, flags=re.DOTALL)

    out_path = output_dir / "dashboard.html"
    out_path.write_text(built, encoding="utf-8")
    return out_path


def open_dashboard(path: Path) -> None:
    """Open the dashboard HTML file in the default browser."""
    webbrowser.open(Path(path).as_uri())
