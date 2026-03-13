"""LLM-powered contextual Q&A for custom form fields."""
from __future__ import annotations
from typing import Any

import requests


def _build_prompt(question: str, job_description: str, resume_text: str) -> str:
    return (
        f"You are helping a job applicant answer a custom question on a job application form.\n\n"
        f"Job description:\n{job_description}\n\n"
        f"Applicant's resume:\n{resume_text}\n\n"
        f"Form question: {question}\n\n"
        f"Write a concise, specific 2-3 sentence answer in first person. "
        f"Be honest, professional, and tailored to the job. "
        f"Do not add preamble or sign-off."
    )


def answer_question(
    question: str,
    job_description: str,
    resume_text: str,
    config: dict[str, Any],
) -> str:
    """Return a tailored answer string, or '' if provider is none or request fails."""
    provider = config.get("llm_provider", "none")
    if provider == "none":
        return ""

    prompt = _build_prompt(question, job_description, resume_text)

    try:
        if provider == "claude":
            return _call_claude(prompt, config)
        elif provider == "openai":
            return _call_openai(prompt, config)
        elif provider == "custom":
            return _call_custom(prompt, config)
    except Exception:
        return ""

    return ""


def _call_claude(prompt: str, config: dict[str, Any]) -> str:
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": config["llm_api_key"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": config["llm_model"],
            "max_tokens": 200,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def _call_openai(prompt: str, config: dict[str, Any]) -> str:
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {config['llm_api_key']}",
            "content-type": "application/json",
        },
        json={
            "model": config["llm_model"],
            "max_tokens": 200,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_custom(prompt: str, config: dict[str, Any]) -> str:
    base_url = config["llm_custom_url"].rstrip("/")
    auth_header = config.get("llm_custom_auth_header", "")

    headers = {"content-type": "application/json"}
    if ":" in auth_header:
        key, _, val = auth_header.partition(":")
        headers[key.strip()] = val.strip()

    resp = requests.post(
        f"{base_url}/chat/completions",
        headers=headers,
        json={
            "model": config["llm_model"],
            "max_tokens": 200,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
