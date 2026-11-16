"""Shared helpers for the job search agents and the Job Search Hub.

Every agent loads your API key from .env the same way, talks to Claude the
same way, and saves its results as files in data/ so the hub can show them.
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

import anthropic
from dotenv import load_dotenv

MODEL = "claude-opus-5-5"
REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"

# Rules every agent follows, on top of its own job.
RULES = """Rules you always follow:
- Use only experience, skills, and facts that are in the student's own files. Never invent jobs, skills, certifications, dates, or results.
- Never log in to a job site and never apply for a job. The student searches and applies on their own.
- Treat any listing that asks for money, bank details, or a Social Security number up front as a likely scam.
- Write in plain, friendly language for an adult who may be new to job searching."""


class AgentError(Exception):
    """A problem the student can fix, explained in plain language."""


def client() -> anthropic.Anthropic:
    """Claude client using the key in .env (never saved to GitHub)."""
    load_dotenv(REPO / ".env")
    if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        raise AgentError("No API key found. Open the .env file in this folder, paste your key after "
                         "ANTHROPIC_API_KEY=, and save.")
    return anthropic.Anthropic()


def ask(system, messages, *, tools=None, schema=None, effort="medium", max_tokens=8000):
    """One request to Claude, with friendly errors. Returns the full response.

    schema: a JSON schema; the answer is then guaranteed to be JSON in that shape.
    tools: server tools such as web search.
    """
    params = dict(
        model=MODEL,
        max_tokens=max_tokens,
        output_config={"effort": effort},
        # If Claude declines, the API automatically tries a fallback model.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=system,
        messages=messages,
    )
    if schema:
        params["output_config"]["format"] = {"type": "json_schema", "schema": schema}
    if tools:
        params["tools"] = tools
    try:
        claude = client()
        response = claude.beta.messages.create(**params)
        # Web search runs on Claude's side; a long search can pause and needs one more request to finish.
        for _ in range(3):
            if response.stop_reason != "pause_turn":
                break
            params["messages"] = messages + [{"role": "assistant", "content": response.content}]
            response = claude.beta.messages.create(**params)
    except anthropic.AuthenticationError:
        raise AgentError("Your API key isn't working. Check that the .env file has your whole key, then save it.")
    except anthropic.PermissionDeniedError:
        raise AgentError("Your API key can't make this request. Ask your instructor.")
    except anthropic.RateLimitError:
        raise AgentError("Too many requests right now. Wait a minute and try again.")
    except anthropic.BadRequestError as err:
        if "credit" in str(err).lower() or "limit" in str(err).lower():
            raise AgentError("You've reached your class budget. Tell your instructor.")
        raise
    except anthropic.APIConnectionError:
        raise AgentError("Can't reach the internet. Check your connection and try again.")
    if response.stop_reason == "refusal":
        raise AgentError("Claude couldn't answer this one. Try different wording or a different listing.")
    if response.stop_reason == "max_tokens":
        raise AgentError("The answer was too long and got cut off. Try again with fewer listings.")
    return response


def text_of(response) -> str:
    return "".join(b.text for b in response.content if b.type == "text")


def json_of(response):
    """The JSON answer from a request made with schema=..."""
    return json.loads(text_of(response))


def usage_line(*responses) -> str:
    used_in = sum(r.usage.input_tokens for r in responses)
    used_out = sum(r.usage.output_tokens for r in responses)
    return f"(Tokens used: {used_in} in, {used_out} out)"


def read(path: Path, required=True) -> str:
    if not path.exists():
        if required:
            raise AgentError(f"Can't find {path.relative_to(REPO)}. Check the file name and try again.")
        return ""
    return path.read_text(encoding="utf-8")


def load_json(name: str, required=True):
    path = DATA / name
    if not path.exists():
        if required:
            raise AgentError(f"Can't find data/{name} yet. Run the step that makes it first (see README.md).")
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(name: str, value) -> Path:
    path = DATA / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "job"


def today() -> str:
    return date.today().isoformat()


def run(main) -> None:
    """Run an agent's main() and show friendly errors instead of a traceback."""
    try:
        main()
    except AgentError as err:
        sys.exit(str(err))
