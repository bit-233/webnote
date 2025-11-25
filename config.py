import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

APP_CONFIG = {
    "HOST": os.getenv("NOTES_HOST", "0.0.0.0"),
    "PORT": int(os.getenv("NOTES_PORT", "7056")),
    "DATA_DIR": os.getenv("NOTES_DATA_DIR", str(BASE_DIR / "data")),
    "ADMIN_PASSWORD": os.getenv("NOTES_ADMIN_PASSWORD", ""),
    "COOKIE_NAME": "notes_session",
}
