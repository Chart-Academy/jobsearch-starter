# Day 1: Build your Job Search Hub (Agent Lab WO-04, Skills-to-Openings)

Today you build a private website on your computer that finds real job openings for you, ranks them against your must-haves, and keeps your top 10, your application tracker, your résumés, and your cover letters in one place. Your agents do the searching. You check their work, and you do your own applying.

**How to use this page:** copy each prompt into Claude Code, one at a time, in order. Wait until Claude finishes and you've checked the result before you paste the next one. Words in **[brackets]** are yours to choose: change them before you press Enter.

**If something breaks**, paste this:
```
That didn't work. Here is what I saw: [paste the error or describe what happened]. Explain what went wrong in plain language, then fix it.
```

---

## Start of class (type these in the terminal)
Change `jobsearch-yourname` to your repo's name (the one you made on the setup page), then run the line for your computer.

Mac:
```
cd ~/Documents/jobsearch-yourname && git pull && source .venv/bin/activate && pip install -r requirements.txt && claude
```
Windows:
```
cd ~\Documents\jobsearch-yourname; git pull; .venv\Scripts\Activate.ps1; pip install -r requirements.txt; claude
```

## Prompt 1: Get oriented
```
Read CLAUDE.md, NOTES.md, and prompts/DAY1-job-search-hub.md. In five sentences or fewer, explain in plain language what we're building today and what each part does. Don't build anything yet.
```

## Prompt 2: Your résumé
Have your résumé open in Google Docs. You'll paste it into the chat after this prompt.
```
I'm going to paste my résumé next. Save it as data/resume.txt, replacing the sample. Before you save it, remove my phone number, email address, and home address, and tell me exactly what you removed. Don't change anything else.
```

## Prompt 3: About me, in my own words
```
Help me fill in data/about_me.md. Go through it one section at a time: ask me the question, wait for my answer, and write down what I said using my own words. Don't make up answers or add anything I didn't say. Replace each SAMPLE line as we go. When we're done, read the whole file back to me.
```

## Prompt 4: Build the Profile Builder agent
```
Build agents/build_profile.py, my Profile Builder agent.

What it does: reads data/resume.txt and data/about_me.md and saves my skills profile to data/profile.json.
How to build it:
- Use the helpers in agents/common.py, and put the shared RULES text in its instructions.
- Use structured outputs (schema=) so the answer is always JSON with these fields: summary (two sentences), target_roles (list), location, skills (list of {skill, proof}, where proof says where it shows up in my résumé or notes), hidden_skills (skills I have but didn't list, like ones from caregiving, volunteering, or side jobs), certifications, must_haves (exactly as I wrote them), nice_to_haves, start_date, search_terms (3 to 5 job titles or keywords), and notes_still_sample (true if about_me.md still has SAMPLE lines).
- Add today's date as "updated" before saving.
- Print a short, friendly summary: what I'm looking for, my must-haves, my skills, and the hidden skills. If notes_still_sample is true, tell me to finish about_me.md.
- End by printing the next step and the tokens used.
When it's built, run it once and show me the result.
```
**Check it:** is everything in your profile true? If not, fix your résumé or about_me.md and paste: `Run python agents/build_profile.py again.`

## Prompt 5: Build the Opening Finder agent
```
Build agents/find_openings.py, my Opening Finder agent.

What it does: finds real, current job openings that fit my profile, adds the listings I pasted into data/listings_pasted.txt, and saves them all to data/openings.json.
How to build it:
- Use the helpers in agents/common.py and the shared RULES.
- Step 1, search: use Claude's web search tool ({"type": "web_search_20260209", "name": "web_search", "max_uses": 5}) with effort "low". Search for my target_roles and search_terms near my location. Prefer employer career pages, government job boards (USAJOBS, DC Government Careers), and well-known job boards. For each opening: title, employer, location, pay, schedule, the link exactly as it appeared in the results, when it was posted, two or three lines about the job, and any sign of fast hiring. Only report openings actually seen in the search results, and never make up a link. Aim for 10 to 15. Never log in to a site and never apply.
- Step 2, organize: a second request with structured outputs turns the search results plus my pasted listings into one clean list. Each opening has: title, employer, location, pay, schedule, link, posted, source ("web search" or "you pasted"), about, requirements (list), fast_hire_signs (list), and warning_signs (list). Merge exact duplicates. Give each opening an id number starting at 1.
- Skip data/listings_pasted.txt if it still has the sample note at the top. If I run it with --no-search, use only my pasted listings.
- Print a numbered list of what it found, remind me to open each link myself, then print the next step and the tokens used.
When it's built, run it once and show me the result.
```

## Your turn: search on your own
Search Indeed and DC Government Careers yourself for two or three jobs you'd really apply to. Paste each listing (title, employer, pay, description, link) into `data/listings_pasted.txt`, with a line of three dashes (`---`) between listings. Delete the sample note at the top. Then paste:
```
Run python agents/find_openings.py again so it includes the listings I found myself.
```

## Prompt 6: Build the Fit Checker agent
```
Build agents/rank_openings.py, my Fit Checker agent.

What it does: checks every opening in data/openings.json against my profile, labels and scores it, and saves my top 10 to data/top10.json.
How to build it:
- Use the helpers in agents/common.py and the shared RULES. Use structured outputs.
- For every opening: check each of my must-haves as "met", "not met", or "unknown" (unknown is not the same as met), with a short reason. Label it "good fit", "maybe", "not a fit", "scam", "closed", or "duplicate". Scam signs: fees or equipment to buy, pay far above normal for the work, asking for bank details or an SSN before an interview, interviews only by text or chat app, a vague employer, or a personal email address. Mark quick_hire only if the listing mentions open interviews, same-week interviews or offers, on-the-spot hiring, or an immediate start. Give a fit_score from 1 to 10 and a chance of "strong", "fair", or "stretch", based only on how my real skills match the requirements. Add why (one or two sentences), matching_skills, and gaps.
- Combine each opening with its ranking, and add student_check: {"checked": false, "agree": true, "note": ""} so I can record my own check later.
- Sort good fits first, then maybes, each by fit score. top10 = the ids of the first 10 good fits and maybes.
- Save {"updated": today, "top10": [...], "jobs": [...]} to data/top10.json.
- Print my top 10 with scores, labels, and QUICK HIRE; then the ones left out and why. Say that scores are estimates and that I should check every one myself. End with the next step and the tokens used.
When it's built, run it once and show me the result.
```

## Prompt 7: Build the back end (hub.py)
```
Build hub.py, the back end of my Job Search Hub. Follow the Job Search Hub section of CLAUDE.md.

- Python standard library only (http.server with ThreadingHTTPServer). Listen on 127.0.0.1 port 8000. Serve the files in site/. Print "Open http://localhost:8000 in Chrome" when it starts, and stop cleanly with Ctrl+C.
- GET /api/hub returns JSON: profile (data/profile.json or null), top10, jobs, updated (from data/top10.json, or empty lists), tracker (rows from data/tracker.csv), documents (data/resume.txt plus every .md and .txt file in data/resumes/ and data/cover_letters/, each as {folder, name, title}), and interviews (every JSON file in data/interviews/, or an empty list).
- GET /api/document?folder=...&name=... returns {text} for one of those documents. Refuse any name with a slash or one that starts with a dot.
- POST /api/check {id, checked, agree, note} saves my own check of one job into its student_check in data/top10.json.
- POST /api/tracker/add {id} adds that job from my top 10 to the tracker (Company, Role, Link, QUICK HIRE, Status "Interested") unless it's already there, and returns the tracker.
- POST /api/tracker {rows} saves the whole tracker and returns it.
- Tracker columns, in this order: Company, Role, Link, QUICK HIRE, Date applied, Status, Follow-up date, Interview date, Offer date, Notes. Save it as data/tracker.csv so I can import it into Google Sheets.
- Only accept POST requests whose Host is localhost or 127.0.0.1 and whose Content-Type is application/json. Send errors back as {"error": "..."} in plain language.
Don't start the server yourself. When you're done, tell me how to start it in a second terminal window.
```

## Prompt 8: Build the front end (Jobs page)
Choose your own look first: a name for your hub, a main color, an emoji avatar, and the feeling you want the page to have.
```
Build the front end of my Job Search Hub in site/: index.html, style.css, and hub.js. Plain HTML, CSS, and JavaScript only. Follow the Job Search Hub section of CLAUDE.md.

My choices:
- Name of my hub: [My Job Search Hub]
- Main color: [#3a56a5, or name any color you like]
- Avatar in the header: [🧭, or any emoji you like]
- How the page should feel: [calm and encouraging]

The page shows, top to bottom:
1. A header with my avatar, the hub name, a line saying which jobs I'm searching for, and links to "Jobs" and "Interview practice" (interview.html, which we'll build on day 2).
2. Progress boxes: openings found, top jobs I've checked (like 3/10), jobs in my tracker, applications sent (tracker rows with a status other than Interested), practice interviews, and my average STAR score (or a dash if none yet).
3. "What I'm looking for": my profile summary, target roles, location, must-haves, and nice-to-haves.
4. "My top 10 openings": a card for each job with its rank, title, employer, location, pay, fit score out of 10, chips for the label, the chance, the source, and a highlighted QUICK HIRE chip when it applies, the reason, each must-have marked ✓ met, ✗ not met, or ? unknown, the gaps, an "Open listing" button (new tab, only for http or https links), and "Add to tracker". At the bottom of each card, a check box "I opened it and checked it against my must-haves", an agree/disagree menu, a note box (placeholder: "What did the agent get right or wrong? (your own words)"), and a "Save my check" button. Checked cards turn light green. Above the cards, one line: the scores are estimates, so check every job yourself.
5. A fold-out list of the openings that didn't make my top 10, with their label and reason. Show scam labels in red.
6. "My application tracker": an editable table (Status is a drop-down: Interested, Applied, Interview, Offer, Not selected, Withdrew; the four date columns use date pickers), with buttons to save it, add a job I found myself, remove a row, and "Download for Google Sheets" (a CSV file).
7. "My documents": a list of my résumés and cover letters; clicking one shows it next to the list.
Keep the colors as CSS variables at the top of style.css. Make it easy to read on a laptop and a phone, and escape every value before putting it on the page.
When it's done, tell me how to start the hub and open it.
```

## Start your hub
Open a **second** terminal window, go to your repo folder, activate `.venv` (see Start of class), then run:
```
python hub.py
```
Open **http://localhost:8000** in Chrome. Leave this window open while you use your hub. Press **Ctrl+C** in it to stop the hub.

## Your turn: check every ranking
For each job in your top 10: click **Open listing**, read the real posting, and compare it with your must-haves. Tick the check box, choose agree or disagree, and write in the note box, in your own words, what the agent got right or wrong. Click **Save my check**. Add the jobs you'd really apply to with **Add to tracker**.

## Prompt 9 (optional): Make it yours
```
Change my hub's look: [describe what you want, for example "make the header a sunset gradient", "use a rounded friendly font", "add a short encouraging quote under my name", or "make QUICK HIRE jobs glow"]. Keep everything else working.
```

## Prompt 10 (optional): A cover letter for a job you like
```
Build agents/write_cover_letter.py. Run it as python agents/write_cover_letter.py 3, where 3 is the job's id. It reads my résumé and that job from data/top10.json and drafts a cover letter of under 250 words using only my real experience, with [brackets] where I should add something only I know. Save it to data/cover_letters/ as a .md file named after the employer and job, starting with "DRAFT: edit before you send." Then run it for job [id number].
```
Open the draft in your hub (My documents) and edit it so it's true and sounds like you.

## Prompt 11: Save your work (every time, before you close your laptop)
```
Update NOTES.md with what we did today and what's next. Then commit all my work with a short, clear message and push it to GitHub. Tell me when it's saved.
```

---

## Turn in (Canvas)
1. A link to your GitHub repo (make sure your instructor has access).
2. A screenshot of your hub's top 10 with your checks saved, and a screenshot of your tracker.
3. Your answers to the "In your own words" questions on the course site, typed in the Canvas text box.
