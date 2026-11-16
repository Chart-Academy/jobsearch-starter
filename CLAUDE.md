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

## The Job Search Hub (Agent Labs WO-04 and WO-05)
The student builds a private website on this computer that shows their job search. The class prompts are in `prompts/`; when the student pastes one, follow it closely, keep to the layout below, and don't add extra features.
- `agents/common.py` is provided. Every agent uses its helpers: `ask()` for Claude requests (it handles errors and the refusal fallback), `json_of()`/`text_of()` to read answers, `load_json()`/`save_json()` for files in `data/`, `run()` to show friendly errors, and the shared `RULES` text in every agent's instructions. Use `schema=` (structured outputs) whenever an agent must return data.
- Agents: `agents/build_profile.py` → `data/profile.json`; `agents/find_openings.py` → `data/openings.json`; `agents/rank_openings.py` → `data/top10.json`; `agents/write_cover_letter.py` → `data/cover_letters/`; `agents/interview_coach.py` (day 2).
- Back end: `hub.py` in the repo folder, Python standard library only (`http.server`), listening on `127.0.0.1` port 8000. It serves `site/` and a small JSON API under `/api/`. It only accepts POST requests whose Host is localhost and whose Content-Type is JSON. It is the only part that talks to Claude; the API key never reaches the browser.
- Front end: plain HTML, CSS, and JavaScript in `site/` (no frameworks, no build step, no outside scripts). `site/style.css` keeps the colors as CSS variables at the top so the student can change them. Escape every value before putting it in the page.
- Student files: `data/resume.txt`, `data/about_me.md` (written in the student's own words), `data/listings_pasted.txt` (listings they found themselves), `data/resumes/`, `data/cover_letters/`, `data/tracker.csv`, `data/interviews/`.
- The student starts the hub in a second terminal window with `python hub.py`. Don't run it in your own session (it keeps running until stopped); tell the student how to start it instead.
- When a step is done, tell the student in two or three plain sentences what you built and how to try it.

## Rules
- **Never** write the API key into any file, print it, or ask the student to paste it into the chat.
- Never commit `.env` files, `.venv/`, or personal documents with Social Security numbers, birth dates, home addresses, or bank details.
- Résumé content must describe things the student actually did. Suggest wording; never invent jobs, skills, certifications, or dates.
- Agents may search and organize job listings. They must never log in to a job site or submit an application for the student. Find openings with Claude's web search tool; never scrape Indeed, Google, or any site that doesn't allow it.
- Don't write the student's "In your own words" answers, their notes about the rankings, or their interview answers.
- Each student has a budget of about $20 for the whole course. Keep test runs small, and don't loop over many API calls without asking first.

## Memory between computers
Conversations don't carry over between computers, but this repo does.
- At the start of a session, read `NOTES.md`.
- At the end of a session (or when the student says they're done), update `NOTES.md` with what we did and what's next. Then commit with a short, clear message and push to GitHub.
