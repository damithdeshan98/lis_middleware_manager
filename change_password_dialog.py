from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

import auth_manager
from field_widgets import PasswordField


class ChangePasswordDialog(QDialog):
    """
    Change password dialog.
    - require_current=True  → user changes their own password (old password verified)
    - require_current=False → Admin resets another user's password (no old password needed)
    """

    def __init__(self, username: str, require_current: bool = True, parent=None):
        super().__init__(parent)
        self._username = username
        self._require_current = require_current

        title = (
            "Change Password"
            if require_current
            else f"Reset Password — {username}"
        )
        self.setWindowTitle(title)
        self.setFixedSize(390, 390 if require_current else 320)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self._build_ui()

    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(0)

        # ── Header ──
        title_lbl = QLabel(
            "Change Password" if self._require_current else f"Reset Password"
        )
        title_lbl.setStyleSheet(
            "font-size:16px;font-weight:bold;color:#cdd6f4;background:transparent;"
        )
        layout.addWidget(title_lbl)
        layout.addSpacing(4)

        sub = QLabel(
            f"Enter your current password to set a new one."
            if self._require_current
            else f"Set a new password for <b>{self._username}</b>."
        )
        sub.setStyleSheet("font-size:12px;color:#6c7086;background:transparent;")
        sub.setWordWrap(True)
        layout.addWidget(sub)
        layout.addSpacing(18)

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background:#313244;border:none;")
        layout.addWidget(div)
        layout.addSpacing(16)

        # ── Current password (self-change only) ──
        if self._require_current:
            layout.addWidget(_cap("CURRENT PASSWORD"))
            layout.addSpacing(5)
            self._current_pw = PasswordField("Enter current password")
            layout.addWidget(self._current_pw)
            layout.addSpacing(13)
            self._current_pw.input.returnPressed.connect(
                lambda: self._new_pw.input.setFocus()
            )

        # ── New password ──
        layout.addWidget(_cap("NEW PASSWORD"))
        layout.addSpacing(5)
        self._new_pw = PasswordField("Enter new password")
        layout.addWidget(self._new_pw)
        layout.addSpacing(13)

        # ── Confirm new password ──
        layout.addWidget(_cap("CONFIRM NEW PASSWORD"))
        layout.addSpacing(5)
        self._confirm_pw = PasswordField("Re-enter new password")
        layout.addWidget(self._confirm_pw)

        # ── Error label ──
        layout.addSpacing(10)
        self._error = QLabel()
        self._error.setStyleSheet(
            "font-size:11px;color:#f38ba8;background:transparent;"
        )
        self._error.setWordWrap(True)
        layout.addWidget(self._error)

        layout.addStretch()

        # ── Action buttons ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel = QPushButton("Cancel")
        cancel.setObjectName("cancelBtn")
        cancel.setFixedHeight(38)
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)

        confirm_text = "Change Password" if self._require_current else "Reset Password"
        save_btn = QPushButton(confirm_text)
        save_btn.setObjectName("loginSubmitBtn")
        save_btn.setFixedHeight(38)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn, 1)

        layout.addLayout(btn_row)

        # Keyboard navigation
        self._new_pw.input.returnPressed.connect(
            lambda: self._confirm_pw.input.setFocus()
        )
        self._confirm_pw.input.returnPressed.connect(self._on_save)

        if self._require_current:
            self._current_pw.input.setFocus()
        else:
            self._new_pw.input.setFocus()

    # ------------------------------------------------------------------ #

    def _on_save(self) -> None:
        new_pw   = self._new_pw.text()
        confirm  = self._confirm_pw.text()

        if not new_pw:
            self._error.setText("New password is required.")
            return
        if len(new_pw) < 6:
            self._error.setText("Password must be at least 6 characters.")
            return
        if new_pw != confirm:
            self._error.setText("Passwords do not match.")
            return

        if self._require_current:
            old_pw = self._current_pw.text()
            if not old_pw:
                self._error.setText("Current password is required.")
                return
            if not auth_manager.change_password(self._username, old_pw, new_pw):
                self._error.setText("Current password is incorrect.")
                self._current_pw.clear()
                self._current_pw.setFocus()
                return
        else:
            auth_manager.reset_password(self._username, new_pw)

        self.accept()


# ── Helper ──────────────────────────────────────────────────────── #

def _cap(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        "font-size:10px;font-weight:bold;color:#6c7086;"
        "letter-spacing:1.5px;background:transparent;"
    )
    return lbl
