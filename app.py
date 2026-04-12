import json
import os
from pathlib import Path
from flask import Flask, request

app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "tiny-notes-app")
APP_MESSAGE = os.getenv("APP_MESSAGE", "no-secret")
DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
NOTES_FILE = DATA_DIR / "notes.json"


def load_notes():
    if not NOTES_FILE.exists():
        return []

    try:
        return json.loads(NOTES_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_notes(notes):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    NOTES_FILE.write_text(
        json.dumps(notes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


@app.get("/healthz")
def healthz():
    return {"status": "ok"}, 200


@app.get("/readyz")
def readyz():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not NOTES_FILE.exists():
        NOTES_FILE.write_text("[]", encoding="utf-8")
    return {"status": "ready"}, 200



@app.get("/notes")
def list_notes():
    return {"notes": load_notes()}, 200


@app.post("/notes")
def create_note():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "").strip()

    if not text:
        return {"error": "text is required"}, 400

    notes = load_notes()
    note = {"id": len(notes) + 1, "text": text}
    notes.append(note)
    save_notes(notes)
    return note, 201


@app.get("/")
def index():
    return f"""
    <p>Version: v3</p>
    <h1>{APP_NAME}</h1>
    <p>App is running.</p>
    <p>Use /notes, /healthz, /readyz</p>
    <p>Secret message: {APP_MESSAGE}</p>
    """, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
