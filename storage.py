import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from config import APP_CONFIG

DATA_DIR = Path(APP_CONFIG["DATA_DIR"])
NOTES_DIR = DATA_DIR / "notes"


def ensure_dirs() -> None:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _note_path(note_id: str) -> Path:
    return NOTES_DIR / f"{note_id}.json"


def list_notes(query: str = "", tag: str = "") -> List[dict]:
    ensure_dirs()
    notes = []
    for file in NOTES_DIR.glob("*.json"):
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
            notes.append(data)
        except Exception:
            continue
    if query:
        notes = [n for n in notes if query.lower() in n.get("title", "").lower()]
    if tag:
        notes = [n for n in notes if tag in n.get("tags", [])]
    notes.sort(key=lambda n: n.get("updated_at", n.get("created_at", "")), reverse=True)
    return notes


def get_note(note_id: str) -> Optional[dict]:
    path = _note_path(note_id)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def create_note(title: str, content: str, tags: Optional[List[str]] = None) -> dict:
    ensure_dirs()
    now = _now_iso()
    sanitized_title = title.strip() or "未命名笔记"
    note_id = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    note = {
        "id": note_id,
        "title": sanitized_title,
        "content": content,
        "tags": tags or [],
        "created_at": now,
        "updated_at": now,
    }
    _note_path(note_id).write_text(json.dumps(note, ensure_ascii=False, indent=2), encoding="utf-8")
    return note


def update_note(note_id: str, title: str, content: str, tags: Optional[List[str]] = None) -> Optional[dict]:
    note = get_note(note_id)
    if not note:
        return None
    note["title"] = title.strip() or "未命名笔记"
    note["content"] = content
    note["tags"] = tags or []
    note["updated_at"] = _now_iso()
    _note_path(note_id).write_text(json.dumps(note, ensure_ascii=False, indent=2), encoding="utf-8")
    return note


def delete_note(note_id: str) -> bool:
    path = _note_path(note_id)
    if not path.exists():
        return False
    path.unlink()
    return True
