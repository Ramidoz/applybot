# ApplyBot

Automate your job search pipeline — for any profession.

## Quick start

### Technical users
```bash
pip install applybot
applybot init          # 2-min guided wizard
applybot run --dry-run # test without submitting
applybot run           # go live
```

### Non-technical users
Double-click `installers/install.bat` (Windows) or `installers/install.sh` (Mac/Linux).

## Commands

| Command | What it does |
|---|---|
| `applybot init` | Guided setup wizard |
| `applybot login linkedin` | Save LinkedIn session (for auto-apply) |
| `applybot run` | Full pipeline |
| `applybot run --dry-run` | Test without submitting |
| `applybot run --no-apply` | Scrape + generate docs only |
| `applybot status` | Print status table in terminal |
| `applybot dashboard` | Rebuild + open dashboard |

## Configuration

All settings live in `applybot.json` (created by `applybot init`).
Never commit this file — it contains your API key.

## Browser automation (Plan 2)

Auto-apply to LinkedIn Easy Apply, Greenhouse, and Lever requires:
```bash
pip install "applybot[browser]"
playwright install chrome
```
