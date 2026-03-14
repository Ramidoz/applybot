[![PyPI](https://img.shields.io/pypi/v/applybot)](https://pypi.org/project/applybot/)


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

## Browser automation

Auto-apply to LinkedIn Easy Apply, Greenhouse, and Lever.

**Setup (one time):**
```bash
pip install "applybot[browser]"
playwright install chrome
applybot login linkedin    # opens Chrome — log in, then close the window
```

Cookies are saved to `sessions/linkedin_cookies.json`. Keep this file private.

**Supported platforms:**
- LinkedIn Easy Apply
- Greenhouse
- Lever

## LLM setup (optional)

ApplyBot can use an LLM to answer open-text custom questions on application forms.

Set `llm_provider` in `applybot.json` to one of:

| Provider | Description |
|---|---|
| `none` (default) | Skip custom questions — fill manually |
| `claude` | Anthropic Claude (requires `llm_api_key`) |
| `openai` | OpenAI GPT (requires `llm_api_key`) |
| `custom` | Any OpenAI-compatible endpoint (set `llm_custom_url`) |

Example config for Claude:
```json
{
  "llm_provider": "claude",
  "llm_api_key": "sk-ant-...",
  "llm_model": "claude-haiku-4-5-20251001"
}
```
