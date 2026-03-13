"""Tests for contextual.py — LLM-powered Q&A for custom form fields."""
import pytest
import responses as responses_lib
from unittest.mock import patch, MagicMock

from applybot.contextual import answer_question, _build_prompt


# --- _build_prompt ---

def test_build_prompt_contains_question():
    prompt = _build_prompt("What is your biggest strength?", "data scientist job", "my resume")
    assert "What is your biggest strength?" in prompt


def test_build_prompt_contains_resume():
    prompt = _build_prompt("Why do you want this role?", "ml engineer", "Python expert resume")
    assert "Python expert resume" in prompt


def test_build_prompt_contains_job_description():
    prompt = _build_prompt("Why apply?", "exciting ML startup job", "my resume")
    assert "exciting ML startup job" in prompt


# --- answer_question: provider=none ---

def test_answer_question_none_provider_returns_empty():
    config = {"llm_provider": "none"}
    result = answer_question("What motivates you?", "job desc", "resume text", config)
    assert result == ""


def test_answer_question_unknown_provider_returns_empty():
    config = {"llm_provider": "gemini"}
    result = answer_question("What motivates you?", "job desc", "resume text", config)
    assert result == ""


# --- answer_question: provider=claude ---

@responses_lib.activate
def test_answer_question_claude_calls_api():
    responses_lib.add(
        responses_lib.POST,
        "https://api.anthropic.com/v1/messages",
        json={"content": [{"text": "I thrive in collaborative environments."}]},
        status=200,
    )
    config = {
        "llm_provider": "claude",
        "llm_api_key": "sk-test",
        "llm_model": "claude-haiku-4-5-20251001",
    }
    result = answer_question("What motivates you?", "job desc", "resume text", config)
    assert "collaborative" in result


# --- answer_question: provider=openai ---

@responses_lib.activate
def test_answer_question_openai_calls_api():
    responses_lib.add(
        responses_lib.POST,
        "https://api.openai.com/v1/chat/completions",
        json={"choices": [{"message": {"content": "I enjoy solving hard problems."}}]},
        status=200,
    )
    config = {
        "llm_provider": "openai",
        "llm_api_key": "sk-openai-test",
        "llm_model": "gpt-4o-mini",
    }
    result = answer_question("Describe your experience.", "job desc", "resume text", config)
    assert "hard problems" in result


# --- answer_question: provider=custom ---

@responses_lib.activate
def test_answer_question_custom_calls_configured_url():
    responses_lib.add(
        responses_lib.POST,
        "http://localhost:11434/v1/chat/completions",
        json={"choices": [{"message": {"content": "Custom LLM answer."}}]},
        status=200,
    )
    config = {
        "llm_provider": "custom",
        "llm_api_key": "",
        "llm_model": "llama3",
        "llm_custom_url": "http://localhost:11434/v1",
        "llm_custom_auth_header": "Authorization: Bearer local",
    }
    result = answer_question("Tell us about yourself.", "job desc", "resume text", config)
    assert "Custom LLM" in result


# --- error handling ---

@responses_lib.activate
def test_answer_question_api_error_returns_empty():
    responses_lib.add(
        responses_lib.POST,
        "https://api.anthropic.com/v1/messages",
        status=500,
    )
    config = {
        "llm_provider": "claude",
        "llm_api_key": "sk-test",
        "llm_model": "claude-haiku-4-5-20251001",
    }
    result = answer_question("What is your strength?", "job desc", "resume text", config)
    assert result == ""
