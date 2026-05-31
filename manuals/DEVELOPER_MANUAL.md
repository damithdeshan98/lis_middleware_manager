# LIS Middleware Manager — Developer Manual

Technical reference for developers working on the **LIS Middleware Manager** — a
PyQt6 desktop application for running and monitoring Java JAR middleware services.

> **Audience:** Python developers maintaining or extending this codebase.
> Assumes familiarity with Python 3.10+, basic Qt concepts (signals/slots,
> the event loop), and the Windows process model.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Technology Stack](#2-technology-stack)
3. [Development Setup](#3-development-setup)
4. [Project Layout](#4-project-layout)
5. [Architecture](#5-architecture)
6. [Module Reference](#6-module-reference)
7. [Data & Persistence](#7-data--persistence)
8. [Process Lifecycle](#8-process-lifecycle)
9. [Authentication & Security](#9-authentication--security)
10. [Role-Based Access Control](#10-role-based-access-control)
11. [UI & Styling Conventions](#11-ui--styling-conventions)
12. [Coding Conventions](#12-coding-conventions)
13. [Extending the Application](#13-extending-the-application)
14. [Build & Distribution](#14-build--distribution)
15. [Known Limitations & Gotchas](#15-known-limitations--gotchas)

---

## 1. Overview

The application launches a login dialog, then a main window that manages a set of
Java middleware processes. Each service is a `java -jar <path>` invocation wrapped in
a Qt `QProcess`. The UI streams stdout/stderr live, persists logs to disk,
auto-restarts crashed services, and gates destructive actions behind an Admin role.

There is **no build step, no framework scaffolding, and no test suite** — it is a
flat collection of single-responsibility modules wired together in `main.py`.

---

## 2. Technology Stack

| Concern | Choice |
|---|---|
| Language | Python **3.10+** (uses `X | Y` union syntax, `dict[str, T]` generics) |
| UI toolkit | **PyQt6** (`>=6.4.0`) — the only third-party dependency |
| Child-process management | `QProcess` (async I/O) + `subprocess.run` (for `taskkill`) |
| Password hashing | `hashlib.pbkdf2_hmac` (SHA-256, 260 000 iterations) |
| Secure comparison / salts | `secrets` (`compare_digest`, `token_bytes`) |
| Persistence | Plain **JSON** files in the user's home directory |
| Target platform | **Windows 10/11** (process-tree kill is Windows-specific) |

---

## 3. Development Setup

```bash
# 1. Clone
git clone https://github.com/damithdeshan98/lis_middleware_manager.git
cd lis_middleware_manager

# 2. Virtual environment (recommended)
python -m venv venv
venv\Scripts\activate          # PowerShell: venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt   # just PyQt6

# 4. Run
python main.py
```

To run the JAR services you manage, **Java (JRE/JDK)** must be installed and on
`PATH` — the app shells out to the bare command `java`.

There are no linters, formatters, or tests configured in the repo. The code targets
CPython on Windows; the only OS-specific branch is the `taskkill` call in
`process_worker.py` (a `kill()` fallback exists for non-Windows).

---

## 4. Project Layout

```
lis_middleware_manager/
│
├── main.py                      # Entry point: QApplication, login gate, main window
│
├── main_window.py               # MainWindow + ServiceCardWidget (the core UI)
├── process_worker.py            # MiddlewareProcess: QProcess wrapper per service
├── config_manager.py            # load/save service config; defines paths & LOGS_DIR
│
├── auth_manager.py              # User store: hashing, verify, CRUD (no UI)
├── login_dialog.py              # Login + first-run "Create Account" dialog
├── add_user_dialog.py           # Add-user form (Admin)
├── user_manager_dialog.py       # User list with add/remove/reset (Admin)
├── change_password_dialog.py    # Change (self) / reset (admin) password dialog
├── field_widgets.py             # Reusable TextField / PasswordField widgets
│
├── styles.py                    # Global Qt stylesheet (STYLESHEET string, dark theme)
├── icon.py                      # create_app_icon(): microscope icon drawn at runtime
│
├── requirements.txt             # PyQt6>=6.4.0
├── run.vbs                      # Windows launcher (runs pythonw.exe silently)
├── lis_icon.ico                 # Icon file (for shortcut / packaging)
└── README.md
```

> ⚠️ The log directory name is intentionally spelled **`middlewere_logs`** (note the
> "e") in `config_manager.py`. Match the existing constant — don't "fix" it casually
> or you'll orphan existing log files.

---

## 5. Architecture

### Layering

```
            main.py  (composition root)
                │
        ┌───────┴────────┐
   LoginDialog       MainWindow ──────────────┐
        │                │                     │
   auth_manager     ServiceCardWidget   dialogs (user mgmt,
   (user store)     (per-service UI)     change pw, add user)
                         │                     │
                  MiddlewareProcess       auth_manager
                  (QProcess wrapper)
                         │
                  config_manager (JSON persistence + LOGS_DIR)
```

### Key principles

- **UI ↔ logic separation.** `auth_manager.py` and `config_manager.py` are pure
  logic/persistence modules with **no Qt imports**. All Qt/UI lives in the
  `*_dialog.py`, `main_window.py`, `field_widgets.py`, `styles.py`, `icon.py` files.
- **Signal-driven process updates.** `MiddlewareProcess` is a `QObject` that emits
  `status_changed` and `log_received` signals. `MainWindow` connects to them; the
  process layer never touches widgets directly.
- **Module-level session state.** The logged-in user is held in
  `auth_manager._session_user` (module global), set on successful login and read via
  `get_current_user()`.

### Startup flow (`main.py`)

1. Create `QApplication`, set name, global `STYLESHEET`, default font, window icon.
2. Show `LoginDialog` modally. If it isn't `Accepted`, `sys.exit(0)`.
3. Read `(username, role)` from `auth_manager.get_current_user()`.
4. Construct and show `MainWindow(username, role)`.
5. Enter the Qt event loop via `app.exec()`.

---

## 6. Module Reference

### `main.py`
Composition root. Wires the login gate to the main window. No business logic.

### `config_manager.py`
- `CONFIG_FILE = ~/.middleware_manager/config.json`
- `LOGS_DIR = <project>/middlewere_logs` — **created at import time**.
- `load_config() -> list[dict]` — returns `[]` on any error (corrupt/missing file).
- `save_config(entries)` — writes pretty-printed JSON, creating the parent dir.

Each config entry: `{"id", "name", "jar_path", "auto_restart"}`.

### `process_worker.py` — `MiddlewareProcess(QObject)`
Wraps one `QProcess`. See [Process Lifecycle](#8-process-lifecycle). Signals:
- `status_changed(str id, str status_value)`
- `log_received(str id, str html_fragment)`

Key fields: `id`, `name`, `jar_path`, `auto_restart`, `status` (`Status` enum),
`_user_stopped`, `_stopped_at` (monotonic timestamp), `_log_file`.

Constants: `RESTART_DELAY_MS = 3000`, `PORT_RELEASE_DELAY_MS = 2000`.

### `main_window.py`
- `ServiceCardWidget(QWidget)` — sidebar card with status dot, labels, and
  start/stop/remove buttons. `set_status()` recolours and toggles button enablement.
- `MainWindow(QMainWindow)` — owns dicts keyed by service id (`mid`):
  `_processes`, `_cards`, `_list_items`, `_logs`. Builds the top bar, sidebar, log
  panel, and status bar; handles all user actions; persists via `_save()`.
  `closeEvent` disables auto-restart and stops every process before exiting.

### `auth_manager.py`
Pure logic user store (no Qt). See [Authentication](#9-authentication--security).
Public API: `credentials_exist`, `user_exists`, `save_credentials`, `add_user`,
`remove_user`, `list_users`, `verify_credentials`, `get_current_user`,
`change_password`, `reset_password`.

### Dialogs
- `login_dialog.py` — dual-mode: **setup** (no users exist → "Create Account",
  first account forced to Admin) vs **sign-in**. Validates length/match, calls
  `save_credentials` / `verify_credentials`.
- `add_user_dialog.py` — Admin add-user form; validates and calls `add_user`.
- `user_manager_dialog.py` — scrollable user list; add/remove/reset; blocks removing
  your own account.
- `change_password_dialog.py` — `require_current=True` → self-change (verifies old
  pw via `change_password`); `require_current=False` → admin reset (`reset_password`).

### `field_widgets.py`
`TextField` and `PasswordField` — framed `QLineEdit` wrappers with a focus-border
highlight (via an event filter) and, for passwords, a 👁 show/hide toggle. Expose
`.input` (the `QLineEdit`) and `.text()`.

### `styles.py`
Single `STYLESHEET` string applied app-wide in `main.py`. Dark theme; widgets are
targeted by `objectName` (e.g. `startBtn`, `loginSubmitBtn`, `typeBtn`).

### `icon.py`
`create_app_icon() -> QIcon` renders a microscope icon at several sizes with
`QPainter` — no image asset needed at runtime (`lis_icon.ico` is for packaging).

---

## 7. Data & Persistence

| File | Path | Written by | Format |
|---|---|---|---|
| User store | `~/.middleware_manager/auth.json` | `auth_manager` | JSON list of user dicts |
| Service config | `~/.middleware_manager/config.json` | `config_manager` | JSON list of service dicts |
| Logs | `<project>/middlewere_logs/<safe_name>.log` | `MiddlewareProcess` | Append-only text |

**User dict:** `{"username", "hash", "salt", "role"}` — `hash` and `salt` are hex
strings; `role` ∈ `{"Admin", "General"}`.

**Service dict:** `{"id", "name", "jar_path", "auto_restart"}` — `id` is a
`uuid.uuid4()` string generated when the JAR is added.

**Legacy migration:** `auth_manager._load_users()` auto-migrates the old single-user
format (a bare dict with `"username"`) into a one-element list. Preserve this if you
change the schema.

**Log file naming:** the display name is sanitised with `re.sub(r"[^\w\-.]", "_", name)`
to form `<safe_name>.log`. Distinct names that sanitise to the same string will share
a file — keep this in mind if you add validation.

All reads are defensively wrapped in `try/except` returning empty defaults, so
corrupt or missing files never crash the app.

---

## 8. Process Lifecycle

State machine on the `Status` enum: `STOPPED → RUNNING → (CRASHED → RUNNING) | STOPPED`.

### Start (`start()` → `_do_start()`)
1. No-op if a `QProcess` is already running.
2. Clear `_user_stopped`.
3. **Port-release guard:** if less than `PORT_RELEASE_DELAY_MS` (2 s) has passed since
   the last stop, log a "waiting…" message and defer `_do_start()` via
   `QTimer.singleShot`. This gives the OS time to free a bound TCP port before
   relaunching.
4. `_do_start()` opens the per-service log file (append mode), writes a dated session
   banner, creates a `QProcess` with working dir = `LOGS_DIR`, wires the four
   callbacks (`readyReadStandardOutput`, `readyReadStandardError`, `finished`,
   `errorOccurred`), runs `java -jar <jar_path>`, sets `RUNNING`, and emits.

### Output (`_on_stdout` / `_on_stderr`)
Raw bytes are decoded UTF-8 (`errors="replace"`), written+flushed to the log file,
HTML-escaped, newline-converted to `<br>`, timestamped, and emitted as
`log_received`. stdout renders white (`#cdd6f4`); stderr renders orange (`#fab387`).

### Stop (`stop()`)
Sets `_user_stopped = True`. On Windows, resolves the PID and runs
`taskkill /F /PID <pid> /T` — the `/T` flag kills the **entire process tree**, which
is essential because `java -jar` may spawn child JVMs that would otherwise be
orphaned. On other platforms it falls back to `QProcess.kill()`.

### Exit (`_on_finished`)
- If `_user_stopped` → `_set_stopped(exit_code)` (records `_stopped_at`, closes log,
  emits `STOPPED`).
- Else if `auto_restart` → mark `CRASHED`, log, and `QTimer.singleShot(3000, _restart)`.
- Else → `_set_stopped`.

`_restart()` re-checks `_user_stopped` before calling `start()` to avoid racing a
user-initiated stop.

> **Auto-restart toggling:** confirmation flows in `MainWindow` (`_confirm_stop`,
> `_remove`, `_on_stop_all`, `closeEvent`) set `proc.auto_restart = False` *before*
> `stop()` so a deliberate stop is never treated as a crash. This is the single most
> important invariant when adding new stop paths.

---

## 9. Authentication & Security

- **Hashing:** `pbkdf2_hmac("sha256", password, salt, 260_000)`, stored as hex.
  260 000 iterations follows the OWASP 2023 recommendation.
- **Salt:** unique per user, `secrets.token_bytes(32)`, stored hex; a fresh salt is
  generated on every password change/reset.
- **Verification:** `secrets.compare_digest` for timing-safe hash comparison.
- **At-rest:** only `hash` + `salt` are persisted — never the plaintext password.
- **Session:** the authenticated user dict is held in the module global
  `_session_user`; `get_current_user()` returns `(username, role)`, defaulting to
  `("", "General")` if unset.

### Security notes / hardening opportunities
- No rate-limiting or lockout on failed logins.
- The auth file is world-readable within the user's home dir (no OS ACL hardening).
- `auth.json` integrity is not protected — anyone with file access can edit roles.
- These are acceptable for the single-workstation lab use case but worth knowing
  before any networked deployment.

---

## 10. Role-Based Access Control

RBAC is **UI-gating only**, driven by the `role` string passed to `MainWindow`. There
is no enforcement layer below the UI — actions are simply hidden/disabled for
non-Admins:

| Capability | Gate location |
|---|---|
| `+ Add JAR` button | `_make_topbar` — added only if `role == "Admin"` |
| `👥 Users` button | `_make_topbar` — Admin only |
| Per-card `✕ Remove` | `_register` — `remove_btn.hide()` when not Admin |
| `Clear` log button | `_make_log_panel` — hidden when not Admin |
| Remove **own** account | `user_manager_dialog._make_row` — disabled for current user |

If you add a privileged action, gate it the same way (check `self._role == "Admin"`)
**and** consider whether `auth_manager`/`config_manager` should enforce it too.

---

## 11. UI & Styling Conventions

- **Single global stylesheet.** `styles.py::STYLESHEET` is applied once in `main.py`.
  Widgets opt into styles via `setObjectName(...)`; selectors use `#objectName`.
  Add a new styled widget by giving it an object name and a matching rule.
- **Inline styles** are used for one-off, dynamic, or per-instance styling (status
  colours, role chips, avatar colours). Colour palette is the Catppuccin-style set:
  `#cdd6f4` (text), `#89b4fa` (accent/Admin), `#a6e3a1` (green/General/running),
  `#fab387` (orange/stderr), `#f38ba8` (red/crashed), `#6c7086`/`#45475a` (muted).
- **Reusable fields.** Use `TextField` / `PasswordField` from `field_widgets.py`
  rather than raw `QLineEdit` for consistent focus borders and the password toggle.
- **Keyboard flow.** Dialogs wire `returnPressed` to advance focus / submit; set
  initial focus in `_build_ui`.
- **Icon.** Use `create_app_icon()` for any new top-level window so the microscope
  icon is consistent.

---

## 12. Coding Conventions

- **Type hints** throughout, using 3.10 syntax (`str | None`, `dict[str, T]`).
- **Private members** prefixed `_`; UI-construction helpers named `_make_*` /
  `_build_ui`; event handlers named `_on_*`.
- **Qt slots** decorated with `@pyqtSlot(...)` where the signal signature matters.
- **Defensive persistence** — wrap file reads in `try/except`, return safe defaults.
- **HTML escaping** — always route process/user text through
  `MiddlewareProcess._esc` before inserting into the log `QTextEdit`, which renders
  HTML.
- **Section banners** — modules use `# ─── … ───` comment dividers; match the style
  when adding sections.

---

## 13. Extending the Application

### Add a per-service setting (e.g. custom JVM args)
1. Add the field to the service dict in `MainWindow._save()` and read it in
   `_load_saved()`.
2. Thread it through `MiddlewareProcess.__init__` and into `setArguments(...)` in
   `_do_start`.
3. Surface it in the add-JAR flow (`_on_add`) or a new edit dialog.

### Add a new role / permission
1. Extend the role set (currently `"Admin"`/`"General"`) in `auth_manager`,
   `login_dialog`, `add_user_dialog`.
2. Add UI gates in `MainWindow` / dialogs following [§10](#10-role-based-access-control).

### Add a new managed-action button
1. Build the button in `_make_topbar` (or a card), gate by role.
2. Connect to an `_on_*` handler; for destructive actions show a
   `QMessageBox.warning` confirmation and set `auto_restart = False` before any stop.

### Cross-platform support
The only Windows-specific code is the `taskkill /T` branch in
`MiddlewareProcess.stop()`. A POSIX path already falls back to `QProcess.kill()`, but
for true process-tree termination on Linux/macOS you'd need process-group handling
(e.g. `os.killpg` with a new session).

---

## 14. Build & Distribution

The repo currently ships as **source + a launcher**:

- **`run.vbs`** starts the app with `pythonw.exe` (no console window). Note its
  hard-coded Python path — update it per machine, or replace with a relative/venv
  launcher.
- **`LIS Middleware Manager.lnk`** is a Windows shortcut, and **`lis_icon.ico`** is
  the icon for it / for packaging.

To produce a standalone executable, **PyInstaller** is the natural fit, e.g.:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --icon lis_icon.ico --name "LIS Middleware Manager" main.py
```

Because `icon.py` draws the in-app icon programmatically and the only data files
(`auth.json`, `config.json`) live in the user's home dir, no `--add-data` bundling is
required for normal operation. Verify Java is still found on `PATH` from the packaged
build.

---

## 15. Known Limitations & Gotchas

- **`middlewere_logs` is misspelled** — keep using the existing constant in
  `config_manager.py`; renaming orphans existing logs.
- **`LOGS_DIR` is created at import time** of `config_manager`, so importing it has a
  filesystem side effect.
- **In-memory logs grow unbounded.** `MainWindow._logs[mid]` accumulates HTML
  fragments for the lifetime of the window; only **Clear** (Admin) or removing the
  service frees it. There's no cap or rotation.
- **Log files are append-only and never rotated.** Long-running services produce
  ever-growing `.log` files.
- **No log-file rotation or size cap** for either the on-disk or in-memory logs.
- **RBAC is UI-only** (see [§10](#10-role-based-access-control)) — no enforcement
  beneath the widgets.
- **No automated tests.** Manual verification only; exercise start/stop/crash/restart,
  the port-release wait, and process-tree kill when changing `process_worker.py`.
- **Duplicate import.** `main_window._on_change_password` re-imports `QMessageBox`
  locally; harmless but redundant. (Also note `_on_change_password` exists but is not
  wired to any button in the current top bar.)
- **Single-instance / port conflicts** between services are not detected by the app;
  two services bound to the same port will surface only as crashes in the logs.

---

<div align="center">
  <sub>LIS Middleware Manager · Developer Manual</sub>
</div>
