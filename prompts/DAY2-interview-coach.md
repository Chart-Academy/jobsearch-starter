# Day 2: Add your Interview Coach (Agent Lab WO-05, Interview Practice Coach)

Today you add an Interview practice page to the Job Search Hub you built on day 1. An AI interviewer reads each question out loud, you answer out loud, and your coach gives you STAR feedback (Situation, Task, Action, Result) on every answer. Every practice session is saved, so your hub shows how you're improving.

**How to use this page:** copy each prompt into Claude Code, one at a time, in order. Wait until Claude finishes and you've checked the result before you paste the next one. Words in **[brackets]** are yours to choose: change them before you press Enter.

**If something breaks**, paste this:
```
That didn't work. Here is what I saw: [paste the error or describe what happened]. Explain what went wrong in plain language, then fix it.
```

---

## Start of class (type these in the terminal)
```
cd ~/Documents/<your-repo-name>
git pull
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
claude
```

## Prompt 1: Pick up where you left off
```
Read CLAUDE.md, NOTES.md, and prompts/DAY2-interview-coach.md. In five sentences or fewer, tell me what we built on day 1 and what we'll add today. Don't build anything yet.
```

## Prompt 2: Build the Interview Coach agent
```
Build agents/interview_coach.py, my Interview Coach agent.

It has two functions that the hub will use. Both use the helpers in agents/common.py, the shared RULES, and effort "low".
- next_question(job, asked): acts as a friendly hiring manager for that job (or a general entry-level job if job is None). It asks one question in one or two short sentences that sound natural read out loud, mixes common questions ("Tell me about yourself") with behavioral ones ("Tell me about a time you...") and questions about the job's real requirements, and never repeats a question in asked. It returns the question as plain text.
- star_feedback(job, question, answer): acts as an interview coach and scores one spoken answer with STAR. The answer was spoken and turned into text, so ignore filler words and small transcription mistakes. Use structured outputs with these fields: situation, task, action, result (each {present: true/false, comment}), score (1 to 5: 1 = no STAR parts, 5 = all four, clear and specific), strength, improve, and stronger_version. The stronger version reorganizes only what I actually said into STAR order and puts [brackets] where I need to add something from my own experience. It must never add experience I didn't mention. Add today's date as "date".
Also let me try it in the terminal: python agents/interview_coach.py asks one general question, lets me type an answer, and prints the STAR feedback.
When it's built, tell me how to try it. Don't answer the question for me.
```
**Try it:** run `python agents/interview_coach.py` in the terminal and answer the question yourself.

## Prompt 3: Add interview practice to the back end
```
Add interview practice to hub.py. Keep everything that's already there working.
- POST /api/interview/question {job, asked} returns {question} from next_question.
- POST /api/interview/feedback {job, question, answer} returns {feedback} from star_feedback. If the answer is shorter than 15 characters, send back a friendly error asking me to answer again.
- POST /api/interview/save {job_title, answers} saves {date, job, answers} as a new JSON file in data/interviews/ named with today's date and a number, like 2026-11-18-01.json.
- Import interview_coach only inside these requests, so the Jobs page still works even if something is wrong with the coach.
Don't start the server yourself. Tell me when it's ready.
```

## Prompt 4: Build the Interview practice page
Choose your interviewer first: a name, an avatar, how fast they talk, and how the page should feel.
```
Build site/interview.html and site/interview.js, my Interview practice page. Use the same header, colors, and style.css as my Jobs page, with "Interview practice" highlighted in the menu.

My choices:
- Interviewer's name: [Ms. Johnson]
- Interviewer's avatar: [🧑‍💼, or any emoji you like]
- How fast they talk: [normal] (slower, normal, or faster)
- How the page should feel: [like a real, friendly interview]

The page has:
1. Setup: a menu to pick a job from my top 10 (or "General practice"), how many questions (3, 5, or 6), a "Read questions out loud" check box, and a Start button. A note says to use Chrome or Edge to answer out loud, and that I can always type instead.
2. The interview: "Question 2 of 5", the interviewer's avatar and name with the employer, the question in large text, and a "Say it again" button. The browser reads each question out loud with speechSynthesis.
3. My answer: a microphone button. When I click it, the browser listens (SpeechRecognition, or webkitSpeechRecognition in Chrome) and types what I say into a big text box as I talk; the button turns red and says Stop. I can fix any words in the box before I ask for feedback. If the browser can't listen, or I block the microphone, show a plain message and let me type.
4. A "Get STAR feedback" button. While it waits, show "Your coach is reading your answer…". Then show my score out of 5, four boxes for Situation, Task, Action, and Result (green ✓ if present, red ✗ if missing, each with its comment), "What you did well", "Try next time", and a fold-out "A stronger version, using only what you said".
5. "Next question" until I reach my number of questions, and "Finish and save", which saves the session with /api/interview/save.
6. "My practice history": a table of my saved sessions with the date, job, number of answers, and average STAR score.
Escape every value before putting it on the page. When it's done, tell me how to try it.
```

## Restart your hub
In your second terminal window, press **Ctrl+C** to stop the hub, then start it again so it picks up the new code:
```
python hub.py
```
Open **http://localhost:8000/interview.html** in Chrome and allow the microphone when Chrome asks.

## Your turn: practice
1. Run one **General practice** interview with 3 questions. Answer out loud, in your own words, about things you really did.
2. Run a second interview for a job in your top 10. Use the feedback from the first one.
3. Read your history. What improved?

## Prompt 5 (optional): Make it yours
```
Change my Interview practice page: [describe what you want, for example "show a short tip before each question", "add a timer that shows how long I talked", "make the interviewer's avatar bounce while the question is read", or "add a calm background color"]. Keep everything else working.
```

## Prompt 6: Save your work (every time, before you close your laptop)
```
Update NOTES.md with what we did today and what's next. Then commit all my work with a short, clear message and push it to GitHub. Tell me when it's saved.
```

---

## Turn in (Canvas)
1. A link to your GitHub repo (with your saved practice sessions in data/interviews/).
2. A screenshot of the STAR feedback for one of your answers, and a screenshot of your practice history.
3. Your answers to the "In your own words" questions on the course site, typed in the Canvas text box.
