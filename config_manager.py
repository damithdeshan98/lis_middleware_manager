import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".middleware_manager" / "config.json"


def load_config() -> list[dict]:
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []


def save_config(entries: list[dict]) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
