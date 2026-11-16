"""Cover Letter agent: drafts a cover letter for one job in your top 10.

Run it from the repo folder (with .venv active):
    python agents/write_cover_letter.py 3     # 3 = the job's number in the hub

Reads data/resume.txt, data/profile.json, and data/top10.json. Writes a draft to
data/cover_letters/. It's a draft: edit it so it's true and sounds like you.
"""

import sys

from common import DATA, RULES, AgentError, ask, load_json, read, run, slug, text_of, usage_line

INSTRUCTIONS = f"""You draft a short cover letter (under 250 words) for one job.
Use only experience from the student's résumé and profile. Match their real skills to the job's
requirements in plain, warm language. Leave [brackets] where the student should add a personal detail
only they know, such as why they want to work for this employer.

{RULES}"""


def main() -> None:
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        raise AgentError("Tell me which job: python agents/write_cover_letter.py 3 (the job's number in the hub).")
    job_id = int(sys.argv[1])
    jobs = load_json("top10.json")["jobs"]
    job = next((j for j in jobs if j["id"] == job_id), None)
    if not job:
        raise AgentError(f"There's no job number {job_id} in data/top10.json.")
    resume = read(DATA / "resume.txt")
    response = ask(INSTRUCTIONS, [{"role": "user", "content":
        f"<resume>\n{resume}\n</resume>\n\n<job>\n{job['title']} at {job['employer']} ({job['location']})\n"
        f"{job['about']}\nRequirements: {'; '.join(job['requirements'])}\n"
        f"Their matching skills: {'; '.join(job['matching_skills'])}\n</job>"}])
    letter = text_of(response)
    path = DATA / "cover_letters" / f"{slug(job['employer'] + ' ' + job['title'])}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# Cover letter: {job['title']}, {job['employer']}\n\nDRAFT: edit before you send.\n\n{letter}\n",
                    encoding="utf-8")
    print(letter)
    print(f"\nSaved to {path.relative_to(DATA.parent)}. Edit it so it's true and sounds like you.")
    print(usage_line(response))


if __name__ == "__main__":
    run(main)
