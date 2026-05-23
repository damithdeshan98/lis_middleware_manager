import hashlib
import json
import secrets
from pathlib import Path

AUTH_FILE = Path.home() / ".middleware_manager" / "auth.json"
_ITERATIONS = 260_000  # OWASP 2023 recommendation for PBKDF2-HMAC-SHA256


def _hash_password(password: str, salt: bytes) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return dk.hex()


def credentials_exist() -> bool:
    return AUTH_FILE.exists()


def save_credentials(username: str, password: str, role: str = "Admin") -> None:
    salt = secrets.token_bytes(32)
    pw_hash = _hash_password(password, salt)
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "username": username,
                "hash": pw_hash,
                "salt": salt.hex(),
                "role": role,
            },
            f,
            indent=2,
        )


def verify_credentials(username: str, password: str) -> bool:
    try:
        if not AUTH_FILE.exists():
            return False
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            creds = json.load(f)
        if creds.get("username") != username:
            return False
        salt = bytes.fromhex(creds["salt"])
        expected = _hash_password(password, salt)
        return secrets.compare_digest(expected, creds["hash"])
    except Exception:
        return False


def get_current_user() -> tuple[str, str]:
    """Return (username, role) from stored credentials."""
    try:
        if AUTH_FILE.exists():
            with open(AUTH_FILE, "r", encoding="utf-8") as f:
                creds = json.load(f)
            return creds.get("username", ""), creds.get("role", "General")
    except Exception:
        pass
    return "", "General"
