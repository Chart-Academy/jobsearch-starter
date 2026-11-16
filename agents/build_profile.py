"""Profile Builder agent: turns your résumé and about_me.md into a skills profile.

Run it from the repo folder (with .venv active):
    python agents/build_profile.py

Reads data/resume.txt and data/about_me.md. Writes data/profile.json, which the
other agents and the Job Search Hub use. Check it, and fix anything that's wrong
in your résumé or about_me.md, then run it again.
"""

from common import DATA, RULES, ask, json_of, read, run, save_json, today, usage_line

INSTRUCTIONS = f"""You build a job seeker's skills profile from their résumé and their own notes.
Pull out what they can already do, including skills from caregiving, volunteering, school,
and side jobs that they may not realize count. List their must-haves exactly as they wrote them.

{RULES}"""

SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string", "description": "Two sentences about who they are and what they want."},
        "target_roles": {"type": "array", "items": {"type": "string"}},
        "location": {"type": "string", "description": "Where they want to work and how far they can travel."},
        "skills": {"type": "array", "items": {"type": "object", "properties": {
            "skill": {"type": "string"},
            "proof": {"type": "string", "description": "Where in their résumé or notes this shows up."}},
            "required": ["skill", "proof"], "additionalProperties": False}},
        "hidden_skills": {"type": "array", "items": {"type": "string"},
                          "description": "Skills they have but didn't list as skills, with where they come from."},
        "certifications": {"type": "array", "items": {"type": "string"}},
        "must_haves": {"type": "array", "items": {"type": "string"}},
        "nice_to_haves": {"type": "array", "items": {"type": "string"}},
        "start_date": {"type": "string"},
        "search_terms": {"type": "array", "items": {"type": "string"},
                         "description": "Three to five job titles or keywords to search for."},
        "notes_still_sample": {"type": "boolean",
                               "description": "True if about_me.md still has SAMPLE lines the student hasn't replaced."},
    },
    "required": ["summary", "target_roles", "location", "skills", "hidden_skills", "certifications",
                 "must_haves", "nice_to_haves", "start_date", "search_terms", "notes_still_sample"],
    "additionalProperties": False,
}


def main() -> None:
    resume = read(DATA / "resume.txt")
    about = read(DATA / "about_me.md")
    response = ask(INSTRUCTIONS, [{"role": "user", "content":
        f"<resume>\n{resume}\n</resume>\n\n<about_me>\n{about}\n</about_me>"}], schema=SCHEMA)
    profile = json_of(response)
    profile["updated"] = today()
    save_json("profile.json", profile)

    print("Your skills profile\n")
    print(profile["summary"], "\n")
    print("Looking for:", ", ".join(profile["target_roles"]))
    print("Must-haves:")
    for item in profile["must_haves"]:
        print("  -", item)
    print("Skills:", ", ".join(s["skill"] for s in profile["skills"]))
    if profile["hidden_skills"]:
        print("Skills you may not have noticed:")
        for item in profile["hidden_skills"]:
            print("  -", item)
    if profile["notes_still_sample"]:
        print("\nNote: data/about_me.md still has SAMPLE lines. Replace them with your own words and run this again.")
    print("\nSaved to data/profile.json. Next: python agents/find_openings.py")
    print(usage_line(response))


if __name__ == "__main__":
    run(main)
