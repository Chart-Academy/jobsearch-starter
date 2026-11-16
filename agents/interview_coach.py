"""Interview Coach agent: asks interview questions and gives STAR feedback.

The Job Search Hub's Interview page uses these two functions. You can also try it here:
    python agents/interview_coach.py
"""

from common import RULES, ask, json_of, run, text_of, today

QUESTION_INSTRUCTIONS = f"""You are a friendly hiring manager running a practice interview.
Ask one question at a time, in one or two short sentences that sound natural when read out loud.
Mix common questions ("Tell me about yourself") with behavioral ones ("Tell me about a time you...")
and questions about the job's real requirements. Don't repeat a question already asked.

{RULES}"""

FEEDBACK_INSTRUCTIONS = f"""You are an interview coach. Score one spoken answer with the STAR method:
Situation (the setting), Task (what they had to do), Action (what they did themselves), Result (what happened,
with a number if they have one). The answer was spoken and turned into text, so ignore filler words and
small transcription mistakes. Be encouraging and specific. For the stronger version, reorganize only what the
student actually said into STAR order and mark missing parts with [brackets] for them to fill in from their
own experience. Never add experience they didn't mention.

{RULES}"""

PART = {"type": "object", "properties": {
    "present": {"type": "boolean"}, "comment": {"type": "string"}},
    "required": ["present", "comment"], "additionalProperties": False}
FEEDBACK_SCHEMA = {
    "type": "object",
    "properties": {
        "situation": PART, "task": PART, "action": PART, "result": PART,
        "score": {"type": "integer", "minimum": 1, "maximum": 5,
                  "description": "1 = no STAR parts, 5 = all four, clear and specific."},
        "strength": {"type": "string"},
        "improve": {"type": "string"},
        "stronger_version": {"type": "string"},
    },
    "required": ["situation", "task", "action", "result", "score", "strength", "improve", "stronger_version"],
    "additionalProperties": False,
}


def job_text(job) -> str:
    if not job:
        return "General practice interview for an entry-level job."
    return (f"{job.get('title', '')} at {job.get('employer', '')}\n{job.get('about', '')}\n"
            f"Requirements: {'; '.join(job.get('requirements', []))}")


def next_question(job, asked):
    """The next interview question, as plain text."""
    response = ask(QUESTION_INSTRUCTIONS, [{"role": "user", "content":
        f"<job>\n{job_text(job)}\n</job>\n\nQuestions already asked:\n"
        + ("\n".join(f"- {q}" for q in asked) or "- none yet")
        + "\n\nAsk the next question. Reply with the question only."}], effort="low", max_tokens=2000)
    return text_of(response).strip()


def star_feedback(job, question, answer):
    """STAR feedback for one answer, as a dict (see FEEDBACK_SCHEMA)."""
    response = ask(FEEDBACK_INSTRUCTIONS, [{"role": "user", "content":
        f"<job>\n{job_text(job)}\n</job>\n\n<question>\n{question}\n</question>\n\n<answer>\n{answer}\n</answer>"}],
        schema=FEEDBACK_SCHEMA, effort="low", max_tokens=4000)
    feedback = json_of(response)
    feedback["date"] = today()
    return feedback


def main() -> None:
    question = next_question(None, [])
    print("Interviewer:", question)
    answer = input("\nYour answer (type it, then press Enter):\n> ")
    feedback = star_feedback(None, question, answer)
    print(f"\nSTAR score: {feedback['score']}/5")
    for part in ("situation", "task", "action", "result"):
        mark = "yes" if feedback[part]["present"] else "missing"
        print(f"  {part.title()}: {mark}. {feedback[part]['comment']}")
    print("\nStrength:", feedback["strength"])
    print("Try next time:", feedback["improve"])
    print("\nStronger version:\n" + feedback["stronger_version"])


if __name__ == "__main__":
    run(main)
