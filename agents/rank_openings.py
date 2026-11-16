"""Fit Checker agent: ranks your openings against your must-haves and picks your top 10.

Run it from the repo folder (with .venv active):
    python agents/rank_openings.py

Reads data/profile.json and data/openings.json. Writes data/top10.json, which the
Job Search Hub shows on its Jobs page. Check every ranking yourself in the hub.
"""

from common import RULES, ask, json_of, load_json, run, save_json, today, usage_line

INSTRUCTIONS = f"""You check job openings against one job seeker's profile and rank them.
For every opening:
- Check each must-have: met, not met, or unknown (the listing doesn't say). Unknown is not the same as met.
- Label it: "good fit", "maybe", "not a fit", "scam", "closed", or "duplicate".
  Scam signs: fees or equipment purchases, pay far above normal for the work, requests for bank details
  or an SSN before an interview, interviews only by text or chat app, vague employer, personal email domains.
- Mark QUICK HIRE only if the listing mentions open interviews, same-week interviews or offers,
  on-the-spot hiring, or an immediate start.
- Give a fit score from 1 to 10 and a chance estimate ("strong", "fair", or "stretch") based only on how well
  their real skills match the requirements. This is an estimate, not a promise.
- Explain the score in one or two plain sentences, and list the gaps.

{RULES}"""

RANKING = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "label": {"type": "string", "enum": ["good fit", "maybe", "not a fit", "scam", "closed", "duplicate"]},
        "fit_score": {"type": "integer", "minimum": 1, "maximum": 10},
        "chance": {"type": "string", "enum": ["strong", "fair", "stretch"]},
        "quick_hire": {"type": "boolean"},
        "must_haves": {"type": "array", "items": {"type": "object", "properties": {
            "must_have": {"type": "string"},
            "status": {"type": "string", "enum": ["met", "not met", "unknown"]},
            "why": {"type": "string"}},
            "required": ["must_have", "status", "why"], "additionalProperties": False}},
        "why": {"type": "string"},
        "matching_skills": {"type": "array", "items": {"type": "string"}},
        "gaps": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["id", "label", "fit_score", "chance", "quick_hire", "must_haves", "why", "matching_skills", "gaps"],
    "additionalProperties": False,
}
SCHEMA = {"type": "object", "properties": {"rankings": {"type": "array", "items": RANKING}},
          "required": ["rankings"], "additionalProperties": False}
ORDER = {"good fit": 0, "maybe": 1, "not a fit": 2, "duplicate": 3, "closed": 4, "scam": 5}


def main() -> None:
    profile = load_json("profile.json")
    openings = load_json("openings.json")["openings"]
    listing = "\n\n".join(
        f"[{o['id']}] {o['title']} - {o['employer']} - {o['location']}\nPay: {o['pay'] or 'not listed'}\n"
        f"Schedule: {o['schedule'] or 'not listed'}\nPosted: {o['posted'] or 'not listed'}\nLink: {o['link'] or 'none'}\n"
        f"About: {o['about']}\nRequirements: {'; '.join(o['requirements'])}\n"
        f"Fast-hire signs: {'; '.join(o['fast_hire_signs']) or 'none'}\nWarning signs: {'; '.join(o['warning_signs']) or 'none'}"
        for o in openings)
    profile_text = (f"Summary: {profile['summary']}\nLocation: {profile['location']}\n"
                    f"Must-haves: {'; '.join(profile['must_haves'])}\nNice-to-haves: {'; '.join(profile['nice_to_haves'])}\n"
                    f"Skills: {'; '.join(s['skill'] for s in profile['skills'])}\n"
                    f"Other skills: {'; '.join(profile['hidden_skills'])}\nCertifications: {'; '.join(profile['certifications'])}\n"
                    f"Can start: {profile['start_date']}")
    response = ask(INSTRUCTIONS, [{"role": "user", "content":
        f"<profile>\n{profile_text}\n</profile>\n\n<openings>\n{listing}\n</openings>\n\nRank every opening."}],
        schema=SCHEMA, max_tokens=16000)
    rankings = {r["id"]: r for r in json_of(response)["rankings"] if any(o["id"] == r["id"] for o in openings)}

    jobs = []
    for o in openings:
        r = rankings.get(o["id"])
        if r:
            jobs.append({**o, **r, "student_check": {"checked": False, "agree": True, "note": ""}})
    jobs.sort(key=lambda j: (ORDER[j["label"]], -j["fit_score"]))
    top = [j["id"] for j in jobs if j["label"] in ("good fit", "maybe")][:10]
    save_json("top10.json", {"updated": today(), "top10": top, "jobs": jobs})

    print("Your top openings (an estimate: check each one yourself):\n")
    for j in jobs:
        if j["id"] in top:
            tag = "  QUICK HIRE" if j["quick_hire"] else ""
            print(f"  {j['fit_score']:>2}/10  {j['title']} - {j['employer']} ({j['label']}, {j['chance']} chance){tag}")
    skipped = [j for j in jobs if j["id"] not in top]
    if skipped:
        print("\nLeft out:")
        for j in skipped:
            print(f"  {j['title']} - {j['employer']}: {j['label']}. {j['why']}")
    print("\nSaved to data/top10.json. Open the Job Search Hub to check each ranking: python hub.py")
    print(usage_line(response))


if __name__ == "__main__":
    run(main)
