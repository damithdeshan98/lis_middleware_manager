from datetime import datetime
from enum import Enum

from PyQt6.QtCore import QObject, QProcess, QTimer, pyqtSignal


RESTART_DELAY_MS = 3000


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

    def start(self) -> None:
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            return
        self._user_stopped = False
        self._process = QProcess()
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
            self._process.kill()
        else:
            self._set_stopped(0)

    # ------------------------------------------------------------------ #
    #  Internal helpers
    # ------------------------------------------------------------------ #

    def _set_stopped(self, exit_code: int) -> None:
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
        escaped = self._esc(raw).replace("\r", "").replace("\n", "<br>")
        ts = datetime.now().strftime("%H:%M:%S")
        html = (
            f'<span style="color:#45475a;">[{ts}]</span>'
            f' <span style="color:#cdd6f4;">{escaped}</span>'
        )
        self.log_received.emit(self.id, html)

    def _on_stderr(self) -> None:
        raw = bytes(self._process.readAllStandardError()).decode("utf-8", errors="replace")
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
