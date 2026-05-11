"""
Run the scheduled research prompt and save a review draft.

This script is designed for GitHub Actions. It uses the OpenAI Responses API
with web search enabled, writes a markdown draft for human review, and stores
the raw response metadata beside it.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path


API_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-5"
PROMPT_PATH = Path("prompts/weekly-research.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a weekly research draft.")
    parser.add_argument("--publication-date", default=date.today().isoformat())
    parser.add_argument("--prompt", default=str(PROMPT_PATH))
    parser.add_argument("--output-dir", default="drafts")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", DEFAULT_MODEL))
    return parser.parse_args()


def response_text(payload: dict) -> str:
    if payload.get("output_text"):
        return payload["output_text"].strip()

    parts: list[str] = []
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                parts.append(content["text"])
    return "\n\n".join(parts).strip()


def call_openai(prompt: str, publication_date: str, model: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        if os.getenv("ALLOW_PLACEHOLDER_DRAFT", "").lower() == "true":
            return {
                "id": "placeholder",
                "status": "completed",
                "output_text": placeholder_draft(publication_date),
            }
        raise RuntimeError("OPENAI_API_KEY is required to generate a research draft.")

    request_body = {
        "model": model,
        "reasoning": {"effort": os.getenv("OPENAI_REASONING_EFFORT", "low")},
        "tools": [{"type": "web_search"}],
        "tool_choice": "auto",
        "include": ["web_search_call.action.sources"],
        "input": (
            f"Publication date: {publication_date}\n\n"
            "Run the weekly research process using the instructions below.\n\n"
            f"{prompt}"
        ),
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(request_body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=900) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API request failed: {exc.code} {body}") from exc


def placeholder_draft(publication_date: str) -> str:
    return f"""# The Dungeon Economy Research Draft

Publication date: {publication_date}

## Executive Read

Placeholder draft. Set OPENAI_API_KEY to generate live research.

## This Week's Verified Developments

## Market and Commercial Movement

## Platform and Tooling Signals

## Community Sentiment

## Observations and Interpretation

## Implications by Audience

### Publishers

### Creators

### Platforms

### DMs and Players

## What to Watch Next

## Source Ledger

## Method Note

This placeholder was created without calling the OpenAI API.
"""


def main() -> int:
    args = parse_args()
    prompt = Path(args.prompt).read_text(encoding="utf-8")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = call_openai(prompt, args.publication_date, args.model)
    draft_text = response_text(payload)
    if not draft_text:
        raise RuntimeError("The model response did not contain draft text.")

    md_path = output_dir / f"{args.publication_date}.md"
    json_path = output_dir / f"{args.publication_date}.json"

    md_path.write_text(draft_text + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Draft written to {md_path}")
    print(f"Raw response written to {json_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
