import re
import subprocess
import sys
import time
from datetime import datetime
from enum import Enum
from typing import IO

from PyQt6.QtCore import QObject, QProcess, QTimer, pyqtSignal

from config_manager import LOGS_DIR


RESTART_DELAY_MS = 3000
PORT_RELEASE_DELAY_MS = 2000  # wait after kill for OS to free bound ports


class Status(Enum):
    STOPPED = "Stopped"
    RUNNING = "Running"
    CRASHED = "Crashed"


class MiddlewareProcess(QObject):
    status_changed = pyqtSignal(str, str)  # id, status_value
    log_received = pyqtSignal(str, str)    # id, html_fragment

    def __init__(self, mid: str, name: str, jar_path: str, auto_restart: bool = True):
        super().__init__()
        self.id = mid
        self.name = name
        self.jar_path = jar_path
        self.auto_restart = auto_restart
        self.status = Status.STOPPED
        self._process: QProcess | None = None
        self._user_stopped = False
        self._stopped_at: float = 0.0
        self._log_file: IO | None = None

    def start(self) -> None:
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            return
        self._user_stopped = False
        elapsed_ms = (time.monotonic() - self._stopped_at) * 1000
        remaining_ms = PORT_RELEASE_DELAY_MS - elapsed_ms
        if remaining_ms > 50:
            self._sys_log(
                f"Waiting {int(remaining_ms)}ms for OS to release port&hellip;",
                "#fab387",
            )
            QTimer.singleShot(int(remaining_ms), self._do_start)
            return
        self._do_start()

    def _do_start(self) -> None:
        if self._user_stopped:
            return
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            return
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^\w\-.]", "_", self.name)
        log_path = LOGS_DIR / f"{safe_name}.log"
        self._log_file = open(log_path, "a", encoding="utf-8")
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log_file.write(
            f"\n{'=' * 60}\n[{ts}] Session started — {self.jar_path}\n{'=' * 60}\n"
        )
        self._process = QProcess()
        self._process.setWorkingDirectory(str(LOGS_DIR))
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)
        self._process.errorOccurred.connect(self._on_error)
        self._process.setProgram("java")
        self._process.setArguments(["-jar", self.jar_path])
        self._process.start()
        self.status = Status.RUNNING
        self.status_changed.emit(self.id, Status.RUNNING.value)
        self._sys_log(f"Starting <b>{self._esc(self.name)}</b> &rarr; {self._esc(self.jar_path)}", "#a6e3a1")

    def stop(self) -> None:
        self._user_stopped = True
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            if sys.platform == "win32":
                pid = self._process.processId()
                if pid:
                    subprocess.run(
                        ["taskkill", "/F", "/PID", str(pid), "/T"],
                        capture_output=True,
                    )
            else:
                self._process.kill()
        else:
            self._set_stopped(0)

    # ------------------------------------------------------------------ #
    #  Internal helpers
    # ------------------------------------------------------------------ #

    def _close_log_file(self) -> None:
        if self._log_file:
            self._log_file.close()
            self._log_file = None

    def _set_stopped(self, exit_code: int) -> None:
        self._stopped_at = time.monotonic()
        self._close_log_file()
        self.status = Status.STOPPED
        self.status_changed.emit(self.id, Status.STOPPED.value)
        self._sys_log(f"Stopped (exit code: {exit_code})", "#6c7086")

    @staticmethod
    def _esc(text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _sys_log(self, msg: str, color: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        html = (
            f'<span style="color:#45475a;">[{ts}]</span>'
            f' <span style="color:{color};">{msg}</span><br>'
        )
        self.log_received.emit(self.id, html)

    # ------------------------------------------------------------------ #
    #  QProcess callbacks
    # ------------------------------------------------------------------ #

    def _on_stdout(self) -> None:
        raw = bytes(self._process.readAllStandardOutput()).decode("utf-8", errors="replace")
        if self._log_file:
            self._log_file.write(raw)
            self._log_file.flush()
        escaped = self._esc(raw).replace("\r", "").replace("\n", "<br>")
        ts = datetime.now().strftime("%H:%M:%S")
        html = (
            f'<span style="color:#45475a;">[{ts}]</span>'
            f' <span style="color:#cdd6f4;">{escaped}</span>'
        )
        self.log_received.emit(self.id, html)

    def _on_stderr(self) -> None:
        raw = bytes(self._process.readAllStandardError()).decode("utf-8", errors="replace")
        if self._log_file:
            self._log_file.write(raw)
            self._log_file.flush()
        escaped = self._esc(raw).replace("\r", "").replace("\n", "<br>")
        ts = datetime.now().strftime("%H:%M:%S")
        html = (
            f'<span style="color:#45475a;">[{ts}]</span>'
            f' <span style="color:#fab387;">{escaped}</span>'
        )
        self.log_received.emit(self.id, html)

    def _on_error(self, error: QProcess.ProcessError) -> None:
        messages = {
            QProcess.ProcessError.FailedToStart: "Failed to start — is Java installed and on PATH?",
            QProcess.ProcessError.Crashed: "Process crashed unexpectedly",
            QProcess.ProcessError.Timedout: "Process timed out",
            QProcess.ProcessError.ReadError: "Read error on process pipe",
            QProcess.ProcessError.WriteError: "Write error on process pipe",
            QProcess.ProcessError.UnknownError: "Unknown process error",
        }
        self._sys_log(messages.get(error, "Unknown error"), "#f38ba8")

    def _on_finished(self, exit_code: int, _exit_status) -> None:
        if self._user_stopped:
            self._set_stopped(exit_code)
            return

        if self.auto_restart:
            self._close_log_file()
            self.status = Status.CRASHED
            self.status_changed.emit(self.id, Status.CRASHED.value)
            self._sys_log(
                f"Crashed (exit code: {exit_code}) — restarting in {RESTART_DELAY_MS // 1000}s&hellip;",
                "#f38ba8",
            )
            QTimer.singleShot(RESTART_DELAY_MS, self._restart)
        else:
            self._set_stopped(exit_code)

    def _restart(self) -> None:
        if not self._user_stopped:
            self.start()
