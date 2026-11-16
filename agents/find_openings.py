"""Opening Finder agent: finds real job openings that fit your profile.

Run it from the repo folder (with .venv active):
    python agents/find_openings.py              # web search + listings you pasted
    python agents/find_openings.py --no-search  # only the listings you pasted

It searches the web (it never logs in to a job site or applies for you) and adds
the listings you pasted into data/listings_pasted.txt. Writes data/openings.json.
Next: python agents/rank_openings.py
"""

import sys

from common import DATA, RULES, ask, json_of, load_json, read, run, save_json, text_of, today, usage_line

MAX_SEARCHES = 5  # each web search costs about one cent, plus reading the results

SEARCH_INSTRUCTIONS = f"""You find current, real job openings for a job seeker.
Search for openings that match their target roles and location. Prefer employer career pages,
government job boards (such as USAJOBS and DC Government Careers), and well-known job boards.
For each opening you find, write: job title, employer, location, pay (if listed), schedule (if listed),
the link exactly as it appeared in your search results, when it was posted (if listed), and two or three
lines about the job and its requirements. Note any sign of fast hiring (open interviews, same-week offers,
immediate start). Only report openings you actually saw in search results. Never make up a link.
Aim for 10 to 15 openings.

{RULES}"""

COLLECT_INSTRUCTIONS = f"""You turn job openings into a clean list. You get openings found by web search
and openings the student pasted. Keep every real opening, merge exact duplicates, and copy links exactly.
If an opening has no link, leave the link empty. Never make up a link, pay, or requirement.

{RULES}"""

OPENING = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "employer": {"type": "string"},
        "location": {"type": "string"},
        "pay": {"type": "string", "description": "As listed, or empty if not listed."},
        "schedule": {"type": "string", "description": "As listed, or empty if not listed."},
        "link": {"type": "string"},
        "posted": {"type": "string", "description": "As listed, or empty."},
        "source": {"type": "string", "enum": ["web search", "you pasted"]},
        "about": {"type": "string", "description": "Two or three plain sentences about the job."},
        "requirements": {"type": "array", "items": {"type": "string"}},
        "fast_hire_signs": {"type": "array", "items": {"type": "string"}},
        "warning_signs": {"type": "array", "items": {"type": "string"},
                          "description": "Anything that looks like a scam, a closed listing, or missing details."},
    },
    "required": ["title", "employer", "location", "pay", "schedule", "link", "posted", "source", "about",
                 "requirements", "fast_hire_signs", "warning_signs"],
    "additionalProperties": False,
}
SCHEMA = {"type": "object", "properties": {"openings": {"type": "array", "items": OPENING}},
          "required": ["openings"], "additionalProperties": False}


def main() -> None:
    search = "--no-search" not in sys.argv[1:]
    profile = load_json("profile.json")
    pasted = read(DATA / "listings_pasted.txt", required=False)
    if "PASTE LISTINGS YOU FOUND YOURSELF" in pasted:
        pasted = ""  # still the sample file
    responses = []
    found = ""
    if search:
        print(f"Searching the web for openings (up to {MAX_SEARCHES} searches)...")
        response = ask(SEARCH_INSTRUCTIONS, [{"role": "user", "content":
            "Find openings for this job seeker.\n"
            f"Target roles: {', '.join(profile['target_roles'])}\n"
            f"Search terms: {', '.join(profile['search_terms'])}\n"
            f"Location: {profile['location']}\n"
            f"Must-haves: {'; '.join(profile['must_haves'])}\n"
            f"Today is {today()}."}],
            tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": MAX_SEARCHES}],
            effort="low", max_tokens=16000)
        responses.append(response)
        found = text_of(response)
    if not found and not pasted:
        sys.exit("No openings to work with. Paste listings into data/listings_pasted.txt, "
                 "or run without --no-search.")

    print("Organizing the openings...")
    response = ask(COLLECT_INSTRUCTIONS, [{"role": "user", "content":
        f"<found_by_web_search>\n{found}\n</found_by_web_search>\n\n"
        f"<pasted_by_student>\n{pasted}\n</pasted_by_student>"}],
        schema=SCHEMA, effort="low", max_tokens=16000)
    responses.append(response)
    openings = json_of(response)["openings"]
    for number, opening in enumerate(openings, 1):
        opening["id"] = number
    save_json("openings.json", {"updated": today(), "searched_web": search, "openings": openings})

    print(f"\nFound {len(openings)} openings:")
    for o in openings:
        print(f"  {o['id']:>2}. {o['title']} - {o['employer']} ({o['location']})")
    print("\nOpen each link yourself before you trust it. Saved to data/openings.json.")
    print("Next: python agents/rank_openings.py")
    print(usage_line(*responses))


if __name__ == "__main__":
    run(main)
