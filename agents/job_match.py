"""Job Match agent: compares your résumé to one job posting.

Run it from the repo folder (with .venv active):
    python agents/job_match.py
    python agents/job_match.py data/resume.txt data/job_posting.txt

It reads two text files and asks Claude how well they match, which skills
line up, what's missing, and how to word your real experience for this job.
"""

import sys
from pathlib import Path

import anthropic

MODEL = "claude-opus-5-5"

INSTRUCTIONS = """You are a career coach helping an entry-level job seeker.
Compare the résumé to the job posting. Reply in plain language, using these sections:

1. Match score: a number from 1 to 10, with one sentence explaining why.
2. Skills that match: the posting's requirements the résumé already shows.
3. Gaps: requirements the résumé doesn't show, and one realistic way to close each.
4. Résumé wording: up to three bullet points the person could use, rewritten
   only from experience that is actually in the résumé. Never invent jobs,
   skills, certifications, or dates.
5. Questions to prepare for: two likely interview questions for this job.

Keep the whole answer under 400 words."""


def read_text(path: Path) -> str:
    if not path.exists():
        sys.exit(f"Can't find {path}. Check the file name and try again.")
    return path.read_text(encoding="utf-8")


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    resume_path = Path(sys.argv[1]) if len(sys.argv) > 1 else repo / "data" / "resume.txt"
    job_path = Path(sys.argv[2]) if len(sys.argv) > 2 else repo / "data" / "job_posting.txt"

    resume = read_text(resume_path)
    job = read_text(job_path)

    client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY from your computer

    try:
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=4000,
            output_config={"effort": "medium"},
            # If Claude declines, the API automatically tries a fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system=INSTRUCTIONS,
            messages=[{
                "role": "user",
                "content": f"<resume>\n{resume}\n</resume>\n\n<job_posting>\n{job}\n</job_posting>",
            }],
        )
    except anthropic.AuthenticationError:
        sys.exit("Your API key isn't working. Check step 3 on the Claude Code Setup page.")
    except anthropic.PermissionDeniedError:
        sys.exit("Your API key can't make this request. Ask your instructor.")
    except anthropic.RateLimitError:
        sys.exit("Too many requests right now. Wait a minute and try again.")
    except anthropic.BadRequestError as err:
        if "credit" in str(err).lower() or "limit" in str(err).lower():
            sys.exit("You've reached your class budget. Tell your instructor.")
        raise
    except anthropic.APIConnectionError:
        sys.exit("Can't reach the internet. Check your connection and try again.")

    if response.stop_reason == "refusal":
        sys.exit("Claude couldn't answer this one. Try a different job posting.")

    answer = "".join(block.text for block in response.content if block.type == "text")
    print(answer)

    used = response.usage
    print(f"\n(Tokens used: {used.input_tokens} in, {used.output_tokens} out)")


if __name__ == "__main__":
    main()
