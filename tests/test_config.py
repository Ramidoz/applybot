import json
import pytest
from applybot.config import load_config, save_config, validate_config, ConfigError

REQUIRED_KEYS = [
    "name", "email", "phone", "linkedin_url", "target_roles",
    "remote_only", "salary_min", "salary_max", "master_resume",
    "autofill", "score_threshold", "llm_provider",
]


def test_load_config_reads_json(tmp_project):
    cfg = load_config(tmp_project / "applybot.json")
    assert cfg["name"] == "Jane Smith"
    assert cfg["target_roles"] == ["Software Engineer", "Backend Engineer"]


def test_load_config_file_not_found(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "applybot.json")


def test_load_config_invalid_json(tmp_path):
    (tmp_path / "applybot.json").write_text("not json {{{")
    with pytest.raises(ConfigError, match="invalid JSON"):
        load_config(tmp_path / "applybot.json")


def test_validate_config_passes_for_valid(sample_config):
    validate_config(sample_config)  # should not raise


def test_validate_config_missing_required_key(sample_config):
    del sample_config["email"]
    with pytest.raises(ConfigError, match="email"):
        validate_config(sample_config)


def test_validate_config_empty_target_roles(sample_config):
    sample_config["target_roles"] = []
    with pytest.raises(ConfigError, match="target_roles"):
        validate_config(sample_config)


def test_validate_config_bad_score_threshold(sample_config):
    sample_config["score_threshold"] = 150
    with pytest.raises(ConfigError, match="score_threshold"):
        validate_config(sample_config)


def test_save_config_writes_json(sample_config, tmp_path):
    path = tmp_path / "applybot.json"
    save_config(sample_config, path)
    loaded = json.loads(path.read_text())
    assert loaded["name"] == "Jane Smith"
