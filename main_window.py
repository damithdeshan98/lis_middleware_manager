import os
import uuid

from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config_manager import load_config, save_config
from process_worker import MiddlewareProcess, Status
from user_manager_dialog import UserManagerDialog


# ──────────────────────────────────────────────────────────────────────────── #
#  Per-service card widget shown inside the list
# ──────────────────────────────────────────────────────────────────────────── #

class ServiceCardWidget(QWidget):
    def __init__(self, mid: str, name: str, jar_path: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.mid = mid
        self.setFixedHeight(74)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # Status dot
        self._dot = QLabel("●")
        self._dot.setFixedWidth(20)
        self._dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dot.setStyleSheet("color: #808080; font-size: 17px;")

        # Info column
        info = QVBoxLayout()
        info.setSpacing(1)
        info.setContentsMargins(0, 0, 0, 0)

        self._name_lbl = QLabel(name)
        self._name_lbl.setStyleSheet("font-weight: bold; font-size: 13px; color: #cdd6f4;")

        self._file_lbl = QLabel(os.path.basename(jar_path))
        self._file_lbl.setStyleSheet("font-size: 11px; color: #9a9a9a;")

        self._status_lbl = QLabel("Stopped")
        self._status_lbl.setStyleSheet("font-size: 11px; color: #9a9a9a;")

        info.addWidget(self._name_lbl)
        info.addWidget(self._file_lbl)
        info.addWidget(self._status_lbl)

        # Buttons
        self.start_btn = QPushButton("▶")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.setFixedSize(34, 34)
        self.start_btn.setToolTip("Start service")

        self.stop_btn = QPushButton("■")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setFixedSize(34, 34)
        self.stop_btn.setToolTip("Stop service")
        self.stop_btn.setEnabled(False)

        self.remove_btn = QPushButton("✕")
        self.remove_btn.setObjectName("removeBtn")
        self.remove_btn.setFixedSize(34, 34)
        self.remove_btn.setToolTip("Remove service")

        layout.addWidget(self._dot)
        layout.addLayout(info, 1)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.remove_btn)

    def set_status(self, status: str) -> None:
        palette = {
            "Running":  ("#a6e3a1", "#a6e3a1"),
            "Stopped":  ("#808080", "#9a9a9a"),
            "Crashed":  ("#f38ba8", "#f38ba8"),
        }
        dot_color, text_color = palette.get(status, ("#585b70", "#6c7086"))
        self._dot.setStyleSheet(f"color: {dot_color}; font-size: 17px;")
        self._status_lbl.setText(status)
        self._status_lbl.setStyleSheet(f"font-size: 11px; color: {text_color};")
        running = status == "Running"
        self.start_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)


# ──────────────────────────────────────────────────────────────────────────── #
#  Main application window
# ──────────────────────────────────────────────────────────────────────────── #

class MainWindow(QMainWindow):
    def __init__(self, username: str = "", role: str = ""):
        super().__init__()
        self._username = username
        self._role = role
        self.setWindowTitle("LIS Middleware Manager")
        self.resize(1200, 720)
        self.setMinimumSize(860, 520)

        self._processes:    dict[str, MiddlewareProcess]  = {}
        self._cards:        dict[str, ServiceCardWidget]  = {}
        self._list_items:   dict[str, QListWidgetItem]    = {}
        self._logs:         dict[str, list[str]]          = {}
        self._selected_id:  str | None = None

        self._build_ui()
        self._load_saved()

    # ------------------------------------------------------------------ #
    #  UI construction
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_topbar())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.addWidget(self._make_sidebar())
        splitter.addWidget(self._make_log_panel())
        splitter.setSizes([300, 900])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter, 1)

        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        self._refresh_statusbar()

    def _make_topbar(self) -> QFrame:
        bar = QFrame()
        bar.setFixedHeight(56)
        bar.setStyleSheet(
            "QFrame { background-color: #4a4a4a; border-bottom: 1px solid #5a5a5a; }"
        )
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(10)

        title = QLabel("⚙  LIS Middleware Manager")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #89b4fa;")
        layout.addWidget(title)
        layout.addStretch()

        self._add_btn = QPushButton("  + Add JAR")
        self._add_btn.setObjectName("addBtn")
        self._add_btn.setFixedHeight(36)
        self._add_btn.clicked.connect(self._on_add)

        self._start_all_btn = QPushButton("▶  Start All")
        self._start_all_btn.setObjectName("startAllBtn")
        self._start_all_btn.setFixedHeight(36)
        self._start_all_btn.clicked.connect(self._on_start_all)

        self._stop_all_btn = QPushButton("■  Stop All")
        self._stop_all_btn.setObjectName("stopAllBtn")
        self._stop_all_btn.setFixedHeight(36)
        self._stop_all_btn.clicked.connect(self._on_stop_all)

        if self._role == "Admin":
            layout.addWidget(self._add_btn)
        layout.addWidget(self._start_all_btn)
        layout.addWidget(self._stop_all_btn)

        # User badge + manage users (Admin only)
        if self._username:
            layout.addSpacing(8)
            sep = QLabel("|")
            sep.setStyleSheet("color: #5a5a5a; font-size: 18px;")
            layout.addWidget(sep)
            layout.addSpacing(6)

            user_lbl = QLabel(f"👤  {self._username}")
            user_lbl.setStyleSheet("font-size: 13px; color: #cdd6f4;")
            layout.addWidget(user_lbl)
            layout.addSpacing(6)

            role_color = "#89b4fa" if self._role == "Admin" else "#a6e3a1"
            role_lbl = QLabel(self._role)
            role_lbl.setStyleSheet(
                f"font-size: 11px; font-weight: bold; color: {role_color};"
                f"background-color: rgba(255,255,255,0.07); border-radius: 4px;"
                f"padding: 2px 8px;"
            )
            layout.addWidget(role_lbl)

            if self._role == "Admin":
                layout.addSpacing(8)
                users_btn = QPushButton("👥  Users")
                users_btn.setObjectName("usersBtn")
                users_btn.setFixedHeight(34)
                users_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                users_btn.clicked.connect(self._on_manage_users)
                layout.addWidget(users_btn)

        return bar

    def _make_sidebar(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("sidebar")
        frame.setMinimumWidth(260)
        frame.setMaximumWidth(420)
        frame.setStyleSheet(
            "QFrame#sidebar { background-color: #4a4a4a; border-right: 1px solid #5a5a5a; }"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        hdr = QLabel("   SERVICES")
        hdr.setFixedHeight(36)
        hdr.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #9a9a9a;"
            "letter-spacing: 1px; border-bottom: 1px solid #5a5a5a;"
            "background-color: #4a4a4a; padding-left: 12px;"
        )
        layout.addWidget(hdr)

        self._list = QListWidget()
        self._list.setSpacing(0)
        self._list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._list.currentItemChanged.connect(self._on_selection_changed)
        layout.addWidget(self._list, 1)
        return frame

    def _make_log_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("logPanel")
        frame.setStyleSheet("QFrame#logPanel { background-color: #3a3a3a; }")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header row
        hdr = QFrame()
        hdr.setFixedHeight(44)
        hdr.setStyleSheet(
            "background-color: #4a4a4a; border-bottom: 1px solid #5a5a5a;"
        )
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(16, 6, 16, 6)

        self._log_title = QLabel("Select a service to view logs")
        self._log_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #cdd6f4;")

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setObjectName("clearLogBtn")
        self._clear_btn.setFixedHeight(28)
        self._clear_btn.clicked.connect(self._on_clear_log)
        if self._role != "Admin":
            self._clear_btn.hide()

        hdr_layout.addWidget(self._log_title)
        hdr_layout.addStretch()
        hdr_layout.addWidget(self._clear_btn)
        layout.addWidget(hdr)

        # Log text area
        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self._log_view.document().setDefaultStyleSheet(
            "body { margin: 0; padding: 0; }"
            "p, span { margin: 0; padding: 0; }"
        )
        layout.addWidget(self._log_view, 1)

        # Empty state overlay
        empty_hint = (
            "No service selected\n\nClick  + Add JAR  to get started"
            if self._role == "Admin"
            else "No service selected"
        )
        self._empty_lbl = QLabel(empty_hint)
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_lbl.setStyleSheet(
            "color: #6a6a6a; font-size: 15px; background-color: #3a3a3a;"
        )
        self._empty_lbl.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self._empty_lbl)

        self._log_view.hide()
        return frame

    # ------------------------------------------------------------------ #
    #  Service registration / removal
    # ------------------------------------------------------------------ #

    def _register(self, mid: str, name: str, jar_path: str, auto_restart: bool = True) -> None:
        proc = MiddlewareProcess(mid, name, jar_path, auto_restart)
        proc.status_changed.connect(self._on_status_changed)
        proc.log_received.connect(self._on_log_received)
        self._processes[mid] = proc
        self._logs[mid] = []

        card = ServiceCardWidget(mid, name, jar_path)
        card.start_btn.clicked.connect(lambda: self._processes[mid].start())
        card.stop_btn.clicked.connect(lambda: self._confirm_stop(mid))
        card.remove_btn.clicked.connect(lambda: self._remove(mid))
        if self._role != "Admin":
            card.remove_btn.hide()
        self._cards[mid] = card

        item = QListWidgetItem(self._list)
        item.setData(Qt.ItemDataRole.UserRole, mid)
        item.setSizeHint(QSize(0, 78))
        self._list.addItem(item)
        self._list.setItemWidget(item, card)
        self._list_items[mid] = item

        if len(self._processes) == 1:
            self._list.setCurrentItem(item)

        self._refresh_statusbar()

    def _confirm_stop(self, mid: str) -> None:
        proc = self._processes.get(mid)
        if not proc:
            return
        reply = QMessageBox.warning(
            self,
            "Stop Service",
            f"Are you sure you want to stop <b>{proc.name}</b>?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            proc.auto_restart = False
            proc.stop()

    def _remove(self, mid: str) -> None:
        proc = self._processes.get(mid)
        if not proc:
            return

        if proc.status == Status.RUNNING:
            msg = (
                f"<b>{proc.name}</b> is currently running.<br><br>"
                "Stop it and remove from the list?"
            )
        else:
            msg = f"Are you sure you want to remove <b>{proc.name}</b>?"

        reply = QMessageBox.warning(
            self,
            "Remove Service",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        if proc.status == Status.RUNNING:
            proc.auto_restart = False
            proc.stop()

        item = self._list_items.pop(mid, None)
        if item:
            self._list.takeItem(self._list.row(item))

        self._processes.pop(mid, None)
        self._cards.pop(mid, None)
        self._logs.pop(mid, None)

        if self._selected_id == mid:
            self._selected_id = None
            self._log_title.setText("Select a service to view logs")
            self._log_view.clear()
            self._log_view.hide()
            self._empty_lbl.show()

        self._save()
        self._refresh_statusbar()

    # ------------------------------------------------------------------ #
    #  UI event handlers
    # ------------------------------------------------------------------ #

    def _on_manage_users(self) -> None:
        dlg = UserManagerDialog(current_username=self._username, parent=self)
        dlg.exec()

    def _on_add(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select JAR File(s)", "", "JAR Files (*.jar);;All Files (*)"
        )
        for jar_path in paths:
            default_name = os.path.splitext(os.path.basename(jar_path))[0]
            name, ok = QInputDialog.getText(
                self,
                "Service Name",
                f"Display name for  {os.path.basename(jar_path)}:",
                text=default_name,
            )
            if ok and name.strip():
                self._register(str(uuid.uuid4()), name.strip(), jar_path)
                self._save()

    def _on_start_all(self) -> None:
        for proc in self._processes.values():
            if proc.status == Status.STOPPED:
                proc.start()

    def _on_stop_all(self) -> None:
        active = [p for p in self._processes.values() if p.status != Status.STOPPED]
        if not active:
            return
        count = len(active)
        reply = QMessageBox.warning(
            self,
            "Stop All Services",
            f"Are you sure you want to stop all <b>{count}</b> running service(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        for proc in active:
            proc.auto_restart = False
            proc.stop()

    def _on_clear_log(self) -> None:
        if self._selected_id:
            self._logs[self._selected_id] = []
            self._log_view.clear()

    def _on_selection_changed(
        self, current: QListWidgetItem, _previous: QListWidgetItem
    ) -> None:
        if not current:
            return
        mid: str = current.data(Qt.ItemDataRole.UserRole)
        self._selected_id = mid

        proc = self._processes.get(mid)
        self._log_title.setText(f"Logs — {proc.name}" if proc else "Logs")

        self._log_view.clear()
        logs = self._logs.get(mid, [])
        if logs:
            self._log_view.setHtml("".join(logs))
            sb = self._log_view.verticalScrollBar()
            sb.setValue(sb.maximum())

        self._log_view.show()
        self._empty_lbl.hide()

    # ------------------------------------------------------------------ #
    #  Process signal handlers
    # ------------------------------------------------------------------ #

    @pyqtSlot(str, str)
    def _on_status_changed(self, mid: str, status: str) -> None:
        card = self._cards.get(mid)
        if card:
            card.set_status(status)
        self._refresh_statusbar()

    @pyqtSlot(str, str)
    def _on_log_received(self, mid: str, html: str) -> None:
        self._logs.setdefault(mid, []).append(html)
        if self._selected_id == mid:
            cursor = self._log_view.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertHtml(html)
            self._log_view.setTextCursor(cursor)
            self._log_view.ensureCursorVisible()

    # ------------------------------------------------------------------ #
    #  Persistence & misc
    # ------------------------------------------------------------------ #

    def _load_saved(self) -> None:
        for entry in load_config():
            self._register(
                entry["id"],
                entry["name"],
                entry["jar_path"],
                entry.get("auto_restart", True),
            )

    def _save(self) -> None:
        save_config(
            [
                {
                    "id": mid,
                    "name": p.name,
                    "jar_path": p.jar_path,
                    "auto_restart": p.auto_restart,
                }
                for mid, p in self._processes.items()
            ]
        )

    def _refresh_statusbar(self) -> None:
        running = sum(1 for p in self._processes.values() if p.status == Status.RUNNING)
        total = len(self._processes)
        crashed = sum(1 for p in self._processes.values() if p.status == Status.CRASHED)
        parts = [f"{running} running", f"{total - running} stopped"]
        if crashed:
            parts.append(f"{crashed} crashed")
        self._statusbar.showMessage("   " + "  ·  ".join(parts))

    def closeEvent(self, event) -> None:
        for proc in self._processes.values():
            proc.auto_restart = False
            proc.stop()
        event.accept()
