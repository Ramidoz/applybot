#!/usr/bin/env bash
set -euo pipefail

echo "============================================"
echo " ApplyBot Installer"
echo "============================================"
echo

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Install it from https://python.org/downloads/ or via your package manager."
    exit 1
fi

PYVER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYMAJ=$(python3 -c "import sys; print(sys.version_info.major)")
PYMIN=$(python3 -c "import sys; print(sys.version_info.minor)")

if [[ "$PYMAJ" -lt 3 ]] || ( [[ "$PYMAJ" -eq 3 ]] && [[ "$PYMIN" -lt 9 ]] ); then
    echo "ERROR: Python 3.9 or higher required. Found $PYVER"
    exit 1
fi

echo "Python $PYVER found. OK."
echo

# Install base applybot
echo "Installing ApplyBot..."
pip3 install --upgrade applybot
echo

# Ask about browser automation
# Use '|| true' so pressing Enter (empty input) does not abort under set -euo pipefail
BROWSER=""
read -r -p "Enable browser auto-apply? (LinkedIn, Greenhouse, Lever) [y/N]: " BROWSER || true

# Use tr for lowercase — compatible with bash 3.2 (default on macOS)
BROWSER_LC=$(echo "$BROWSER" | tr '[:upper:]' '[:lower:]')

if [[ "$BROWSER_LC" == "y" ]]; then
    echo "Installing Playwright..."
    pip3 install "applybot[browser]"
    echo "Installing Chrome browser for Playwright..."
    playwright install chrome
    echo "Browser automation enabled."
    echo
    echo "Next: run  applybot login linkedin  to save your LinkedIn session."
    echo
fi

echo "============================================"
echo " ApplyBot installed successfully!"
echo "============================================"
echo
echo "Get started:"
echo "  applybot init          -- run the setup wizard"
echo "  applybot run --dry-run -- test without submitting"
echo "  applybot run           -- go live"
echo
