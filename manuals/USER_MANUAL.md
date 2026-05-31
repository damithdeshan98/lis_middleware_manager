# LIS Middleware Manager — User Manual

A guide to installing, logging in, and using the **LIS Middleware Manager** desktop
application to run and monitor your laboratory middleware (Java JAR) services.

> **Audience:** Lab technicians, IT staff, and administrators who operate the
> middleware services on a Windows workstation. No programming knowledge required.

---

## Table of Contents

1. [What This Application Does](#1-what-this-application-does)
2. [Installing & Launching](#2-installing--launching)
3. [First Launch — Creating Your Account](#3-first-launch--creating-your-account)
4. [Logging In](#4-logging-in)
5. [User Roles](#5-user-roles)
6. [The Main Window](#6-the-main-window)
7. [Managing Services](#7-managing-services)
8. [Viewing Logs](#8-viewing-logs)
9. [Auto-Restart on Crash](#9-auto-restart-on-crash)
10. [Managing Users (Admin)](#10-managing-users-admin)
11. [Passwords](#11-passwords)
12. [Where Your Data Is Stored](#12-where-your-data-is-stored)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. What This Application Does

LIS Middleware Manager lets you run several Java middleware programs (`.jar` files)
from one window. For each service you can:

- **Start** and **Stop** it with a single click.
- Watch its **live output (logs)** as it runs.
- Have it **automatically restart** if it crashes.
- Start or stop **all services at once**.

It also has a **login screen** so only authorised people can operate the services,
and **two levels of access** (Admin and General).

---

## 2. Installing & Launching

### Requirements

- **Windows 10 or 11**
- **Java** (JRE or JDK) installed and available on the system `PATH`
  — this is what actually runs your `.jar` services.
- **Python 3.10+** (only needed if you run from source rather than a packaged build).

### Launching the app

Depending on how it was installed on your machine, do **one** of the following:

| If you have… | Do this |
|---|---|
| A desktop shortcut (`LIS Middleware Manager`) | Double-click it. |
| The project folder | Double-click **`run.vbs`** (starts silently, no console window). |
| A command prompt | Run `python main.py` inside the project folder. |

> If nothing happens when you start the app, see [Troubleshooting](#13-troubleshooting).

---

## 3. First Launch — Creating Your Account

The very first time the application runs, there are no user accounts yet, so it
shows a **Create Account** screen instead of a login screen.

1. Enter a **Username**.
2. Enter a **Password** — must be **at least 6 characters**.
3. **Re-enter** the same password to confirm.
4. The account type is locked to **Admin** — the first account is always an
   administrator.
5. Click **Create Account**.

You are now logged in and the main window opens. From now on, every launch shows
the normal **Sign In** screen.

> 💡 You can use the **👁 (eye)** button next to any password box to show or hide
> what you typed.

---

## 4. Logging In

On every launch after setup, the **Sign In** screen appears.

1. Type your **Username** and **Password**.
2. Press **Enter** or click **Sign In**.

If the credentials are wrong, a red warning appears and the password box clears so
you can try again. If you close the login window without signing in, the app exits.

---

## 5. User Roles

There are two roles. They determine which buttons and features you can see and use.

| Action | Admin | General |
|---|:---:|:---:|
| View services & logs | ✅ | ✅ |
| Start / Stop services | ✅ | ✅ |
| Start All / Stop All | ✅ | ✅ |
| Add a JAR service | ✅ | ❌ |
| Remove a service | ✅ | ❌ |
| Clear a log view | ✅ | ❌ |
| Manage users | ✅ | ❌ |
| Reset other users' passwords | ✅ | ❌ |

A **General** user can operate the existing services (start/stop and watch logs)
but cannot change which services exist or manage accounts. Admin-only buttons are
simply hidden for General users.

Your username and role are shown in the **top-right corner** of the main window.

---

## 6. The Main Window

```
┌──────────────────────────────────────────────────────────────────────┐
│ 🔬 LIS Middleware Manager        [+ Add JAR][▶ Start All][■ Stop All]  │  ← Top bar
│                                  | username  [Admin]  [👥 Users]        │
├───────────────────────┬──────────────────────────────────────────────┤
│ SERVICES              │ Logs — My Service                  [Clear]     │  ← Log header
│ ┌───────────────────┐ │                                                │
│ │ ● Service A   ▶■✕ │ │  [10:14:02] Starting My Service → app.jar      │
│ │   app.jar         │ │  [10:14:03] Server listening on port 8080      │  ← Live logs
│ │   Running         │ │  ...                                           │
│ └───────────────────┘ │                                                │
│ (sidebar list)        │ (log panel)                                    │
├───────────────────────┴──────────────────────────────────────────────┤
│   2 running  ·  1 stopped  ·  0 crashed                                │  ← Status bar
└──────────────────────────────────────────────────────────────────────┘
```

- **Top bar** — app title plus the global action buttons and your user badge.
- **Sidebar (left)** — one card per registered service. Click a card to view its logs.
- **Log panel (right)** — live output for the selected service.
- **Status bar (bottom)** — a running tally of how many services are running,
  stopped, or crashed.

---

## 7. Managing Services

### Adding a service *(Admin only)*

1. Click **+ Add JAR** in the top bar.
2. Browse to and select one or more `.jar` files. (You can pick several at once.)
3. For each file, a box asks for a **display name** — the friendly name shown in the
   sidebar. The file name is suggested by default. Edit it if you like and click **OK**.
4. The service appears in the sidebar, ready to start.

Added services are saved automatically and will reappear the next time you open the
app.

### Each service card

Every card in the sidebar shows:

- **A coloured status dot** and status label:
  - 🟢 **Running** — the service is up.
  - ⚪ **Stopped** — not running.
  - 🔴 **Crashed** — it exited unexpectedly (about to auto-restart).
- The **display name** and the **file name** of the JAR.
- Three buttons:
  - **▶ Start** — starts the service.
  - **■ Stop** — stops it (asks for confirmation first).
  - **✕ Remove** — removes it from the list *(Admin only)*.

### Starting a service

Click the **▶** button on the card. The status dot turns green and logs begin
streaming. If the service was very recently stopped, the app waits up to a couple of
seconds first so the operating system can release the network port — you'll see a
"Waiting … for OS to release port" note in the log.

### Stopping a service

Click the **■** button. You'll be asked **"Are you sure you want to stop …?"** —
click **Yes** to confirm. The service and any Java child processes it started are
fully terminated.

### Start All / Stop All

- **▶ Start All** — starts every service that is currently stopped.
- **■ Stop All** — stops every running service. You'll be asked to confirm, and told
  how many services will be stopped.

### Removing a service *(Admin only)*

Click **✕** on a card. If the service is still running, the app offers to stop it and
remove it. Confirm with **Yes**. Removal updates the saved list immediately.

---

## 8. Viewing Logs

- Click any service card in the sidebar to show its logs in the right-hand panel.
- Output streams **live** while the service runs and auto-scrolls to the latest line.
- Colour coding:
  - **White/grey** — normal program output.
  - **Orange** — error output (the program's standard-error stream).
  - **Green / orange / red** — system messages from the manager (start, waiting,
    crash, etc.).
- Each line is timestamped (`[HH:MM:SS]`).

### Persistent log files

Everything is also written to a log file on disk so you keep a permanent record even
after closing the app. Files live in a **`middlewere_logs`** folder inside the
application directory, one file per service (e.g. `My_Service.log`). Each time a
service starts, a dated separator line is added to its file.

### Clearing a log view *(Admin only)*

Click **Clear** in the log header to empty the on-screen log for the selected
service. This only clears the display — the saved `.log` file on disk is **not**
deleted.

---

## 9. Auto-Restart on Crash

If a running service exits on its own (a crash, rather than you stopping it), the
manager:

1. Marks it **Crashed** (red dot).
2. Logs the exit code and a "restarting in 3s…" message.
3. Waits **3 seconds**, then starts it again automatically.

This keeps essential services alive without manual intervention. If you stop a
service yourself, it stays stopped — auto-restart only reacts to unexpected exits.

---

## 10. Managing Users (Admin)

Admins see a **👥 Users** button in the top bar. Click it to open **User Management**,
where you can:

- See a list of all accounts with their **role** (Admin / General). Your own account
  is tagged **"You"**.
- **+ Add User** — create a new account: choose a username, password (min 6 chars),
  confirm it, and pick **Admin** or **General**.
- **Reset Pwd** — set a new password for any user *without* needing their old one.
- **Remove** — delete an account. You **cannot** remove your own account (the button
  is disabled for your row).

A counter at the bottom shows the total number of users.

---

## 11. Passwords

- **Minimum length:** 6 characters.
- **Show/hide:** use the 👁 button in any password box.
- **Resetting a user's password (Admin):** open **👥 Users → Reset Pwd** on that
  user's row. No old password is required.
- **Forgot the only password / locked out:** see the recovery note in
  [Troubleshooting](#13-troubleshooting).

Your password is never stored as plain text — only a securely hashed version is saved.

---

## 12. Where Your Data Is Stored

All your data lives **outside** the application folder, in your Windows user profile:

| Data | Location |
|---|---|
| User accounts (hashed passwords) | `C:\Users\<you>\.middleware_manager\auth.json` |
| Registered services list | `C:\Users\<you>\.middleware_manager\config.json` |
| Per-service log files | `<application folder>\middlewere_logs\` |

> You normally never need to touch these files. They are listed here for IT staff and
> for password recovery.

---

## 13. Troubleshooting

| Problem | What to do |
|---|---|
| **Service won't start / log says "Failed to start — is Java installed?"** | Java is not installed or not on the `PATH`. Install a JRE/JDK and make sure `java` runs from a command prompt. |
| **Service keeps crashing and restarting** | Open its logs to read the error. The problem is usually in the JAR itself (e.g. a port already in use, missing config). Stop the service to halt the restart loop. |
| **"Waiting … for OS to release port" appears on start** | Normal. The app briefly waits after a stop so the network port frees up before restarting. |
| **App doesn't open at all** | Make sure Python 3.10+ and the PyQt6 dependency are installed, then run `python main.py` from a command prompt to see any error message. |
| **Forgot the password and can't log in** | An Admin can reset it via **👥 Users → Reset Pwd**. If *no one* can log in, an IT person can delete `C:\Users\<you>\.middleware_manager\auth.json`; the next launch will show the **Create Account** screen so you can set up a fresh admin account. (This removes all existing accounts.) |
| **A removed service came back** | Removal is saved instantly. If it reappears, confirm you're logged in as Admin and that you confirmed the removal dialog. |

---

<div align="center">
  <sub>LIS Middleware Manager · User Manual</sub>
</div>
