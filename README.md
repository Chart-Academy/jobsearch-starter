# Job Search Agents

Your project for the Chart Academy Security+ cohort (October 19, 2026). You'll use Claude Code to build small Python agents that help with your job search.

**Setup instructions:** https://chart-academy.github.io/ai-workforce-readiness/claude-code-setup.html

## Start each class
```
cd ~/Documents/<your-repo-name>
git pull
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
claude
```

## Try the sample agent
```
python agents/job_match.py
```
It compares `data/resume.txt` to `data/job_posting.txt`. Both are samples. Replace them with your own résumé and a real job posting.

## Job Search Hub labs
You'll build a private job search website on your computer, one step at a time, by pasting class prompts into Claude Code:
- **Day 1:** [prompts/DAY1-job-search-hub.md](prompts/DAY1-job-search-hub.md). Agents that build your skills profile, find real openings, and rank your top 10, plus your hub's Jobs page with an application tracker and your documents.
- **Day 2:** [prompts/DAY2-interview-coach.md](prompts/DAY2-interview-coach.md). A spoken interview coach that gives you STAR feedback.

Start your hub in a second terminal window with `python hub.py`, then open http://localhost:8000 in Chrome. Only your computer can open it.

## End each class
Ask Claude: *"Update NOTES.md with what we did today and what's next. Then commit and push my work to GitHub."*

## What's here
| File | What it's for |
|---|---|
| `CLAUDE.md` | Instructions Claude reads at the start of every session |
| `NOTES.md` | Your progress log, so you can continue on any computer |
| `prompts/` | The class prompts for the Job Search Hub labs |
| `agents/` | Your agents (Python). `common.py` is a shared toolbox they all use |
| `hub.py`, `site/` | Your Job Search Hub (you build these in the labs) |
| `data/` | Your résumé, notes about the job you want, listings, tracker, cover letters, and interview practice |
| `requirements.txt` | Python packages this project needs |

Never put your API key in any file in this repo.
