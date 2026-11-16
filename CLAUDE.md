# Job Search Agents — Chart Academy, Security+ (October 19, 2026 cohort)

This repo belongs to one student. Together we build small Python agents that help with their job search: matching their résumé to job postings, tracking applications, and preparing for interviews.

## How to work with this student
- Many students are new to coding. Explain what you're about to do in plain language before you do it, and keep each step small.
- Ask what the student wants in their own words before building something. Don't build features they didn't ask for.
- When something fails, explain the error simply and fix it together.

## Project setup
- Python 3 (3.10 or newer, already installed on class computers). The virtual environment is `.venv` in this folder. Activate it before running code:
  - Mac: `source .venv/bin/activate`
  - Windows: `.venv\Scripts\Activate.ps1`
- When you add a package, add it to `requirements.txt` too, so it installs on the student's other computers.
- Agents go in `agents/`. Sample inputs go in `data/`.
- Agents call the Claude API with the `anthropic` package. The student's API key is in `.env` in this folder (`ANTHROPIC_API_KEY=...`). Load it with `python-dotenv` (`load_dotenv()`), then use `anthropic.Anthropic()` with no arguments.
- `.env` is git-ignored and stays on this computer. On a new computer the student copies `.env.example` to `.env` and pastes their key in. If `.env` is missing or empty, tell the student to do that; never ask for the key in chat.

## Rules
- **Never** write the API key into any file, print it, or ask the student to paste it into the chat.
- Never commit `.env` files, `.venv/`, or personal documents with Social Security numbers, birth dates, home addresses, or bank details.
- Résumé content must describe things the student actually did. Suggest wording; never invent jobs, skills, certifications, or dates.
- Agents may search and organize job listings. They must never log in to a job site or submit an application for the student.
- Each student has a budget of about $20 for the whole course. Keep test runs small, and don't loop over many API calls without asking first.

## Memory between computers
Conversations don't carry over between computers, but this repo does.
- At the start of a session, read `NOTES.md`.
- At the end of a session (or when the student says they're done), update `NOTES.md` with what we did and what's next. Then commit with a short, clear message and push to GitHub.
