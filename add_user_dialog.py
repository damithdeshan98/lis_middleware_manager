from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

import auth_manager
from field_widgets import PasswordField, TextField


class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New User")
        self.setFixedSize(400, 490)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self._build_ui()

    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(0)

        # ── Header ──
        title = QLabel("Add New User")
        title.setStyleSheet(
            "font-size:16px;font-weight:bold;color:#cdd6f4;background:transparent;"
        )
        layout.addWidget(title)
        layout.addSpacing(4)

        subtitle = QLabel("Create a new account with access to this application")
        subtitle.setStyleSheet("font-size:12px;color:#6c7086;background:transparent;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        layout.addSpacing(18)

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background:#313244;border:none;")
        layout.addWidget(div)
        layout.addSpacing(16)

        # ── Username ──
        layout.addWidget(_cap("USERNAME"))
        layout.addSpacing(5)
        self._username = TextField("👤", "Enter username")
        layout.addWidget(self._username)
        layout.addSpacing(13)

        # ── Password ──
        layout.addWidget(_cap("PASSWORD"))
        layout.addSpacing(5)
        self._password = PasswordField("Enter password")
        layout.addWidget(self._password)
        layout.addSpacing(13)

        # ── Confirm password ──
        layout.addWidget(_cap("CONFIRM PASSWORD"))
        layout.addSpacing(5)
        self._confirm = PasswordField("Re-enter password")
        layout.addWidget(self._confirm)
        layout.addSpacing(14)

        # ── Account type ──
        layout.addWidget(_cap("ACCOUNT TYPE"))
        layout.addSpacing(6)

        type_row = QHBoxLayout()
        type_row.setSpacing(8)
        type_row.setContentsMargins(0, 0, 0, 0)

        self._admin_btn = QPushButton("Admin")
        self._admin_btn.setObjectName("typeBtn")
        self._admin_btn.setCheckable(True)
        self._admin_btn.setFixedHeight(34)

        self._general_btn = QPushButton("General")
        self._general_btn.setObjectName("typeBtn")
        self._general_btn.setCheckable(True)
        self._general_btn.setChecked(True)
        self._general_btn.setFixedHeight(34)

        grp = QButtonGroup(self)
        grp.setExclusive(True)
        grp.addButton(self._admin_btn)
        grp.addButton(self._general_btn)

        type_row.addWidget(self._admin_btn)
        type_row.addWidget(self._general_btn)
        layout.addLayout(type_row)

        # ── Error ──
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

        create = QPushButton("Create User")
        create.setObjectName("loginSubmitBtn")
        create.setFixedHeight(38)
        create.setCursor(Qt.CursorShape.PointingHandCursor)
        create.clicked.connect(self._on_create)
        btn_row.addWidget(create, 1)

        layout.addLayout(btn_row)

        # Keyboard navigation
        self._username.input.returnPressed.connect(lambda: self._password.input.setFocus())
        self._password.input.returnPressed.connect(lambda: self._confirm.input.setFocus())
        self._confirm.input.returnPressed.connect(self._on_create)
        self._username.input.setFocus()

    # ------------------------------------------------------------------ #

    def _on_create(self) -> None:
        username = self._username.text()
        password = self._password.text()
        confirm  = self._confirm.text()

        if not username:
            self._error.setText("Username is required.")
            return
        if auth_manager.user_exists(username):
            self._error.setText(f"Username '{username}' is already taken.")
            return
        if not password:
            self._error.setText("Password is required.")
            return
        if len(password) < 6:
            self._error.setText("Password must be at least 6 characters.")
            return
        if password != confirm:
            self._error.setText("Passwords do not match.")
            return

        role = "Admin" if self._admin_btn.isChecked() else "General"
        auth_manager.add_user(username, password, role)
        self.accept()


# ── Helper ──────────────────────────────────────────────────────── #

def _cap(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        "font-size:10px;font-weight:bold;color:#6c7086;"
        "letter-spacing:1.5px;background:transparent;"
    )
    return lbl
