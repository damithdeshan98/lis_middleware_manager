<div align="center">

# 🔬 LIS Middleware Manager

**A modern desktop application for managing Laboratory Information System middleware services**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4%2B-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

</div>

---

## Overview

LIS Middleware Manager is a PyQt6 desktop application that lets you run, monitor, and manage multiple Java JAR middleware services from a single interface. It provides real-time log streaming, automatic crash recovery, role-based access control, and secure user authentication — all wrapped in a clean dark-themed UI.

---

## Documentation

| Manual | For | Contents |
|---|---|---|
| 📘 [User Manual](manuals/USER_MANUAL.md) | Operators & lab staff | Install, login, managing services, logs, auto-restart, user management, troubleshooting |
| 📗 [Developer Manual](manuals/DEVELOPER_MANUAL.md) | Maintainers | Architecture, module reference, process lifecycle, authentication, RBAC, build & distribution |

---

## Features

### Process Management
- **Add multiple JAR services** — browse and register any number of Java JAR files
- **Start / Stop individual services** — with confirmation prompts to prevent accidents
- **Start All / Stop All** — control all services in one click
- **Auto-restart on crash** — crashed services automatically restart after 3 seconds
- **Full process tree termination** — uses `taskkill /T` on Windows to kill child JVM processes, ensuring no background Java processes are left behind

### Log Viewer
- **Real-time streaming** — stdout and stderr displayed live as the process runs
- **Per-service log panel** — click any service in the sidebar to view its logs
- **Persistent log files** — logs saved to `middlewere_logs/<service-name>.log`
- **Colour-coded output** — normal output in white, errors in orange, system messages in colour

### Authentication & Security
- **Secure login screen** — shown on every launch
- **PBKDF2-HMAC-SHA256** password hashing with a unique 32-byte random salt per user (260,000 iterations — OWASP 2023 standard)
- **Timing-safe comparison** — uses `secrets.compare_digest` to prevent timing attacks
- **Passwords never stored** — only the hash and salt are saved to disk

### Role-Based Access Control

| Feature | Admin | General |
|---|:---:|:---:|
| View services & logs | ✅ | ✅ |
| Start / Stop services | ✅ | ✅ |
| Add JAR service | ✅ | ❌ |
| Remove service | ✅ | ❌ |
| Clear logs | ✅ | ❌ |
| Change password | ✅ | ❌ |
| Manage users | ✅ | ❌ |
| Reset other users' passwords | ✅ | ❌ |

### User Management *(Admin only)*
- **Add users** — create new Admin or General accounts
- **Remove users** — delete any account except your own
- **Reset passwords** — reset any user's password without knowing the old one
- **User list** — view all registered users with their roles
- **Multi-user support** — unlimited users stored in a single JSON file

---

## Tech Stack

| Component | Technology |
|---|---|
| UI Framework | PyQt6 |
| Language | Python 3.10+ |
| Process Management | QProcess + subprocess (taskkill) |
| Password Hashing | hashlib PBKDF2-HMAC-SHA256 |
| Credential Storage | JSON (`~/.middleware_manager/auth.json`) |
| Service Config | JSON (`~/.middleware_manager/config.json`) |
| Runtime | Java (JRE required for JAR execution) |

---

## Requirements

- Python **3.10** or higher
- Java **JRE/JDK** installed and on `PATH`
- Windows 10 / 11

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/damithdeshan98/lis_middleware_manager.git
cd lis_middleware_manager
```

**2. Create a virtual environment (recommended)**

```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the application**

```bash
python main.py
```

---

## First Launch

On first run, a **Create Account** screen is shown. The first account is always created as **Administrator**.

```
Username  →  choose any username
Password  →  minimum 6 characters
Role      →  Admin (locked for first account)
```

After setup, the login screen appears on every subsequent launch.

> To reset all users (e.g. forgotten password), delete `~/.middleware_manager/auth.json` — the app will show the Create Account screen on next launch.

---

## Project Structure

```
lis_middleware_manager/
│
├── main.py                      # Entry point — launches login then main window
├── main_window.py               # Main application window and service list
├── process_worker.py            # MiddlewareProcess — wraps QProcess for each JAR
├── config_manager.py            # Load/save service configuration
│
├── auth_manager.py              # User credential storage and verification
├── login_dialog.py              # Login / first-time setup dialog
├── add_user_dialog.py           # Add new user form (Admin only)
├── user_manager_dialog.py       # User management list dialog (Admin only)
├── change_password_dialog.py    # Change / reset password dialog (Admin only)
├── field_widgets.py             # Shared styled input field widgets
│
├── styles.py                    # Global Qt stylesheet (dark theme)
├── icon.py                      # Programmatically rendered microscope icon
│
├── manuals/                     # User & developer documentation
│   ├── USER_MANUAL.md
│   └── DEVELOPER_MANUAL.md
│
├── requirements.txt
└── README.md
```

---

## Data Storage

All data is stored **outside the project directory** and is never committed to version control.

| File | Location | Contents |
|---|---|---|
| User credentials | `~/.middleware_manager/auth.json` | Usernames, hashed passwords, roles |
| Service config | `~/.middleware_manager/config.json` | Registered JAR paths and names |
| Log files | `<project>/middlewere_logs/` | Per-service runtime logs |

---

## Security Notes

- Passwords are hashed using **PBKDF2-HMAC-SHA256** with 260,000 iterations
- A unique **32-byte cryptographic salt** is generated per user via `secrets.token_bytes`
- Login uses **`secrets.compare_digest`** to prevent timing side-channel attacks
- Credential files are stored in the user's home directory, outside the project and git repository

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">
  <sub>Built with PyQt6 · Designed for LIS environments</sub>
</div>
