"""Job Search Hub: your private job search website, running on this computer.

Start it from the repo folder (with .venv active):
    python hub.py
Then open http://localhost:8000 in Chrome. Press Ctrl+C here to stop it.

It shows the files your agents saved in data/ and saves your changes back there,
so everything goes to your GitHub repo when you commit and push. Only this computer
can open it. Your API key stays in .env; the web page never sees it.
"""

import csv
import io
import json
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent / "agents"))
from common import DATA, REPO, AgentError, load_json, save_json, today  # noqa: E402

PORT = 8000
SITE = REPO / "site"
TRACKER = DATA / "tracker.csv"
TRACKER_COLUMNS = ["Company", "Role", "Link", "QUICK HIRE", "Date applied", "Status",
                   "Follow-up date", "Interview date", "Offer date", "Notes"]
DOC_FOLDERS = {"resumes": DATA / "resumes", "cover_letters": DATA / "cover_letters"}


def read_tracker():
    if not TRACKER.exists():
        return []
    with TRACKER.open(encoding="utf-8", newline="") as f:
        return [{c: row.get(c, "") for c in TRACKER_COLUMNS} for row in csv.DictReader(f)]


def write_tracker(rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=TRACKER_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({c: str(row.get(c, "")) for c in TRACKER_COLUMNS})
    TRACKER.write_text(buf.getvalue(), encoding="utf-8")


def documents():
    docs = [{"folder": "resumes", "name": "resume.txt", "title": "My résumé"}] if (DATA / "resume.txt").exists() else []
    for folder, path in DOC_FOLDERS.items():
        if path.exists():
            docs += [{"folder": folder, "name": p.name, "title": p.stem.replace("-", " ")}
                     for p in sorted(path.iterdir()) if p.suffix in (".md", ".txt")]
    return docs


def document_path(folder, name):
    base = DATA if (folder == "resumes" and name == "resume.txt") else DOC_FOLDERS.get(folder)
    if not base or "/" in name or "\\" in name or name.startswith("."):
        return None
    path = base / name
    return path if path.exists() else None


def interviews():
    folder = DATA / "interviews"
    if not folder.exists():
        return []
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("*.json"))]


class Hub(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SITE), **kwargs)

    def log_message(self, *args):
        pass  # keep the terminal quiet

    def send_json(self, value, status=200):
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/hub":
            top = load_json("top10.json", required=False) or {"top10": [], "jobs": []}
            return self.send_json({"profile": load_json("profile.json", required=False),
                                   "top10": top["top10"], "jobs": top["jobs"], "updated": top.get("updated"),
                                   "tracker": read_tracker(), "documents": documents(),
                                   "interviews": interviews()})
        if url.path == "/api/document":
            q = parse_qs(url.query)
            path = document_path(q.get("folder", [""])[0], q.get("name", [""])[0])
            if not path:
                return self.send_json({"error": "Document not found."}, 404)
            return self.send_json({"text": path.read_text(encoding="utf-8")})
        return super().do_GET()

    def do_POST(self):
        # Only pages from this hub may save changes.
        host = (self.headers.get("Host") or "").split(":")[0]
        if host not in ("localhost", "127.0.0.1") or "application/json" not in (self.headers.get("Content-Type") or ""):
            return self.send_json({"error": "Not allowed."}, 403)
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
            return self.send_json(self.handle_post(urlparse(self.path).path, body))
        except AgentError as err:
            return self.send_json({"error": str(err)}, 400)
        except (KeyError, ValueError, TypeError):
            return self.send_json({"error": "That request was missing something. Reload the page and try again."}, 400)

    def handle_post(self, path, body):
        if path == "/api/check":  # the student checked one ranking
            top = load_json("top10.json")
            for job in top["jobs"]:
                if job["id"] == int(body["id"]):
                    job["student_check"] = {"checked": bool(body["checked"]), "agree": bool(body["agree"]),
                                            "note": str(body.get("note", ""))[:1000]}
            save_json("top10.json", top)
            return {"ok": True}
        if path == "/api/tracker/add":
            top = load_json("top10.json")
            job = next(j for j in top["jobs"] if j["id"] == int(body["id"]))
            rows = read_tracker()
            if not any(r["Link"] == job["link"] and r["Company"] == job["employer"] for r in rows):
                rows.append({"Company": job["employer"], "Role": job["title"], "Link": job["link"],
                             "QUICK HIRE": "yes" if job["quick_hire"] else "", "Status": "Interested"})
                write_tracker(rows)
            return {"tracker": rows}
        if path == "/api/tracker":
            write_tracker(body["rows"])
            return {"tracker": read_tracker()}
        if path.startswith("/api/interview/"):
            return self.interview(path, body)
        raise KeyError(path)

    def interview(self, path, body):
        from interview_coach import next_question, star_feedback  # loaded only when used
        if path == "/api/interview/question":
            return {"question": next_question(body.get("job"), body.get("asked", []))}
        if path == "/api/interview/feedback":
            answer = str(body["answer"]).strip()
            if len(answer) < 15:
                raise AgentError("That answer is very short. Try answering again, then ask for feedback.")
            return {"feedback": star_feedback(body.get("job"), str(body["question"]), answer)}
        if path == "/api/interview/save":
            folder = DATA / "interviews"
            folder.mkdir(parents=True, exist_ok=True)
            number = len(list(folder.glob("*.json"))) + 1
            session = {"date": today(), "job": body.get("job_title", "General practice"), "answers": body["answers"]}
            (folder / f"{today()}-{number:02d}.json").write_text(
                json.dumps(session, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return {"ok": True}
        raise KeyError(path)


def main():
    if not SITE.exists():
        sys.exit("Can't find the site/ folder. Run this from your repo folder.")
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Hub)
    print(f"Your Job Search Hub is running. Open http://localhost:{PORT} in Chrome.")
    print("Press Ctrl+C to stop it.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nHub stopped.")


if __name__ == "__main__":
    main()
