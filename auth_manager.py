import hashlib
import json
import secrets
from pathlib import Path

AUTH_FILE = Path.home() / ".middleware_manager" / "auth.json"
_ITERATIONS = 260_000  # OWASP 2023 recommendation for PBKDF2-HMAC-SHA256

_session_user: dict | None = None  # set in-memory after successful login


# ── Internal helpers ───────────────────────────────────────────── #

def _hash_password(password: str, salt: bytes) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return dk.hex()


def _load_users() -> list[dict]:
    """Load all users, migrating old single-user format automatically."""
    try:
        if AUTH_FILE.exists():
            with open(AUTH_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Migrate: old format was a plain dict with username/hash/salt/role
            if isinstance(data, dict) and "username" in data:
                return [data]
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def _save_users(users: list[dict]) -> None:
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


# ── Public API ─────────────────────────────────────────────────── #

def credentials_exist() -> bool:
    return bool(_load_users())


def user_exists(username: str) -> bool:
    return any(u.get("username") == username for u in _load_users())


def save_credentials(username: str, password: str, role: str = "Admin") -> None:
    """Create the initial account (first-time setup). Replaces any existing store."""
    salt = secrets.token_bytes(32)
    _save_users([{
        "username": username,
        "hash": _hash_password(password, salt),
        "salt": salt.hex(),
        "role": role,
    }])


def add_user(username: str, password: str, role: str = "General") -> None:
    """Append a new user to the existing user store."""
    users = _load_users()
    salt = secrets.token_bytes(32)
    users.append({
        "username": username,
        "hash": _hash_password(password, salt),
        "salt": salt.hex(),
        "role": role,
    })
    _save_users(users)


def remove_user(username: str) -> bool:
    """Remove a user by username. Returns True if the user was found and removed."""
    users = _load_users()
    filtered = [u for u in users if u.get("username") != username]
    if len(filtered) == len(users):
        return False
    _save_users(filtered)
    return True


def list_users() -> list[dict]:
    """Return [{username, role}] for all users — no password data."""
    return [
        {"username": u.get("username", ""), "role": u.get("role", "General")}
        for u in _load_users()
    ]


def verify_credentials(username: str, password: str) -> bool:
    global _session_user
    try:
        for user in _load_users():
            if user.get("username") != username:
                continue
            salt = bytes.fromhex(user["salt"])
            expected = _hash_password(password, salt)
            if secrets.compare_digest(expected, user["hash"]):
                _session_user = user
                return True
    except Exception:
        pass
    return False


def get_current_user() -> tuple[str, str]:
    """Return (username, role) for the currently logged-in session."""
    if _session_user:
        return _session_user.get("username", ""), _session_user.get("role", "General")
    return "", "General"
