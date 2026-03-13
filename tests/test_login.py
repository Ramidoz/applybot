"""Tests for the applybot login command — cookie saver."""
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from applybot.cli import cli


def test_login_linkedin_saves_cookies(tmp_path, monkeypatch):
    """login linkedin should save cookies to sessions/linkedin_cookies.json."""
    monkeypatch.chdir(tmp_path)

    fake_cookies = [{"name": "li_at", "value": "abc123", "domain": ".linkedin.com"}]

    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_context.cookies.return_value = fake_cookies
    mock_context.new_page.return_value = mock_page
    mock_browser.new_context.return_value = mock_context

    mock_pw = MagicMock()
    mock_pw.chromium.launch.return_value = mock_browser

    mock_sync_playwright = MagicMock()
    mock_sync_playwright.return_value.__enter__ = MagicMock(return_value=mock_pw)
    mock_sync_playwright.return_value.__exit__ = MagicMock(return_value=False)

    with patch("applybot.cli.sync_playwright", mock_sync_playwright):
        runner = CliRunner()
        result = runner.invoke(cli, ["login", "linkedin"])

    assert result.exit_code == 0
    cookies_file = tmp_path / "sessions" / "linkedin_cookies.json"
    assert cookies_file.exists()
    saved = json.loads(cookies_file.read_text())
    assert saved == fake_cookies


def test_login_linkedin_prints_instructions():
    """login linkedin should print instructions telling the user to log in."""
    fake_cookies = [{"name": "li_at", "value": "abc123"}]

    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    mock_context.cookies.return_value = fake_cookies
    mock_context.new_page.return_value = mock_page
    mock_browser.new_context.return_value = mock_context

    mock_pw = MagicMock()
    mock_pw.chromium.launch.return_value = mock_browser

    mock_sync_playwright = MagicMock()
    mock_sync_playwright.return_value.__enter__ = MagicMock(return_value=mock_pw)
    mock_sync_playwright.return_value.__exit__ = MagicMock(return_value=False)

    with patch("applybot.cli.sync_playwright", mock_sync_playwright):
        runner = CliRunner()
        result = runner.invoke(cli, ["login", "linkedin"])

    assert result.exit_code == 0
    assert "linkedin.com" in result.output.lower()
