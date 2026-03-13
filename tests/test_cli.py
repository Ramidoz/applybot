import pytest
from click.testing import CliRunner
from applybot.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_help(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "init" in result.output
    assert "run" in result.output
    assert "status" in result.output
    assert "dashboard" in result.output


def test_cli_version(runner):
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.output


def test_cli_status_empty(runner, tmp_path):
    """status command with no tracker file prints a helpful empty message."""
    import os
    old = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        # Should not crash, should print something useful
        assert len(result.output) > 0
    finally:
        os.chdir(old)
