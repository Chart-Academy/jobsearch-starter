"""Prints the API key from this project's .env file, so Claude Code can use it.

Claude Code runs this through the "apiKeyHelper" setting in .claude/settings.json.
It prints only the key. If the key is missing, it explains how to add it and exits
with an error, so Claude Code shows that message instead of a confusing one.
"""

import sys
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
NAME = "ANTHROPIC_API_KEY"


def main() -> None:
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8-sig").splitlines():
            name, sep, value = line.partition("=")
            if sep and name.strip() == NAME:
                key = value.strip().strip('"').strip("'").strip()
                if key:
                    print(key, end="")
                    return
    sys.stderr.write(
        f"No API key found in {ENV_FILE}. Copy .env.example to .env, "
        f"paste your key after {NAME}=, and save.\n"
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
