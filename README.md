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

## End each class
Ask Claude: *"Update NOTES.md with what we did today and what's next. Then commit and push my work to GitHub."*

## What's here
| File | What it's for |
|---|---|
| `CLAUDE.md` | Instructions Claude reads at the start of every session |
| `NOTES.md` | Your progress log, so you can continue on any computer |
| `agents/` | Your agents (Python) |
| `data/` | Your résumé and job postings |
| `requirements.txt` | Python packages this project needs |

Never put your API key in any file in this repo.
