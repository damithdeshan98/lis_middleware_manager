from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

import auth_manager
from icon import create_app_icon


_CSS_NORMAL  = "QFrame#fieldBox{background:#16161e;border:1.5px solid #313244;border-radius:8px;}"
_CSS_FOCUSED = "QFrame#fieldBox{background:#16161e;border:1.5px solid #89b4fa;border-radius:8px;}"


def _placeholder(field: QLineEdit) -> None:
    pal = field.palette()
    pal.setColor(QPalette.ColorRole.PlaceholderText, QColor("#45475a"))
    field.setPalette(pal)


class _TextField(QFrame):
    """Text input with a left icon and focus-border highlight."""

    def __init__(self, icon: str, placeholder: str, parent=None):
        super().__init__(parent)
        self.setObjectName("fieldBox")
        self.setFixedHeight(48)
        self.setStyleSheet(_CSS_NORMAL)

        row = QHBoxLayout(self)
        row.setContentsMargins(14, 0, 14, 0)
        row.setSpacing(0)

        lbl = QLabel(icon)
        lbl.setFixedWidth(22)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size:15px;color:#585b70;background:transparent;border:none;")
        row.addWidget(lbl)
        row.addSpacing(8)

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setObjectName("fieldInput")
        self.input.setFrame(False)
        _placeholder(self.input)
        row.addWidget(self.input, 1)

        self.input.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.input:
            if event.type() == QEvent.Type.FocusIn:
                self.setStyleSheet(_CSS_FOCUSED)
            elif event.type() == QEvent.Type.FocusOut:
                self.setStyleSheet(_CSS_NORMAL)
        return super().eventFilter(obj, event)

    def text(self) -> str:
        return self.input.text().strip()


class _PasswordField(QFrame):
    """Password input with show/hide toggle and focus-border highlight."""

    def __init__(self, placeholder: str, parent=None):
        super().__init__(parent)
        self.setObjectName("fieldBox")
        self.setFixedHeight(48)
        self.setStyleSheet(_CSS_NORMAL)

        row = QHBoxLayout(self)
        row.setContentsMargins(14, 0, 8, 0)
        row.setSpacing(0)

        lbl = QLabel("🔒")
        lbl.setFixedWidth(22)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size:13px;color:#585b70;background:transparent;border:none;")
        row.addWidget(lbl)
        row.addSpacing(8)

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setEchoMode(QLineEdit.EchoMode.Password)
        self.input.setObjectName("fieldInput")
        self.input.setFrame(False)
        _placeholder(self.input)
        row.addWidget(self.input, 1)

        self._eye = QPushButton("👁")
        self._eye.setObjectName("eyeBtn")
        self._eye.setFixedSize(32, 32)
        self._eye.setCheckable(True)
        self._eye.setToolTip("Show / hide password")
        self._eye.setCursor(Qt.CursorShape.PointingHandCursor)
        self._eye.toggled.connect(self._toggle)
        row.addWidget(self._eye)

        self.input.installEventFilter(self)
        self._eye.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj in (self.input, self._eye):
            if event.type() == QEvent.Type.FocusIn:
                self.setStyleSheet(_CSS_FOCUSED)
            elif event.type() == QEvent.Type.FocusOut:
                self.setStyleSheet(_CSS_NORMAL)
        return super().eventFilter(obj, event)

    def _toggle(self, show: bool) -> None:
        self.input.setEchoMode(
            QLineEdit.EchoMode.Normal if show else QLineEdit.EchoMode.Password
        )
        self.input.setFocus()

    def text(self) -> str:
        return self.input.text()

    def clear(self) -> None:
        self.input.clear()

    def setFocus(self) -> None:
        self.input.setFocus()


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self._setup_mode = not auth_manager.credentials_exist()
        self.setWindowTitle("LIS Middleware Manager")
        self.setFixedSize(420, 680 if self._setup_mode else 515)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self._build_ui()

    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Outer dark background ──
        bg = QFrame()
        bg.setObjectName("loginBg")
        root.addWidget(bg)

        bg_l = QVBoxLayout(bg)
        bg_l.setContentsMargins(26, 26, 26, 26)
        bg_l.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── Card ──
        card = QFrame()
        card.setObjectName("loginCard")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(52)
        shadow.setColor(QColor(0, 0, 0, 170))
        shadow.setOffset(0, 14)
        card.setGraphicsEffect(shadow)
        bg_l.addWidget(card)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(36, 30, 36, 34)
        cl.setSpacing(0)

        # ── App icon ──
        icon_lbl = QLabel()
        icon_lbl.setPixmap(create_app_icon().pixmap(52, 52))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("background:transparent;border:none;")
        cl.addWidget(icon_lbl)
        cl.addSpacing(10)

        # ── App name ──
        title = QLabel("LIS Middleware Manager")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size:18px;font-weight:700;color:#cdd6f4;background:transparent;"
        )
        cl.addWidget(title)
        cl.addSpacing(4)

        subtitle = QLabel(
            "Create your account" if self._setup_mode else "Sign in to continue"
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size:12px;color:#6c7086;background:transparent;")
        cl.addWidget(subtitle)
        cl.addSpacing(22)

        # ── Divider ──
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background:#313244;border:none;")
        cl.addWidget(div)
        cl.addSpacing(20)

        # ── Username ──
        cl.addWidget(self._cap_label("USERNAME"))
        cl.addSpacing(5)
        self._username = _TextField("👤", "Enter your username")
        cl.addWidget(self._username)
        cl.addSpacing(14)

        # ── Password ──
        cl.addWidget(self._cap_label("PASSWORD"))
        cl.addSpacing(5)
        self._password = _PasswordField("Enter your password")
        cl.addWidget(self._password)

        # ── Confirm password (setup only) ──
        if self._setup_mode:
            cl.addSpacing(14)
            cl.addWidget(self._cap_label("CONFIRM PASSWORD"))
            cl.addSpacing(5)
            self._confirm = _PasswordField("Re-enter your password")
            cl.addWidget(self._confirm)
            self._confirm.input.returnPressed.connect(self._on_submit)

            # ── Account type (setup only) ──
            cl.addSpacing(16)
            cl.addWidget(self._cap_label("ACCOUNT TYPE"))
            cl.addSpacing(6)

            type_row = QHBoxLayout()
            type_row.setSpacing(8)
            type_row.setContentsMargins(0, 0, 0, 0)

            self._admin_btn = QPushButton("Admin")
            self._admin_btn.setObjectName("typeBtn")
            self._admin_btn.setCheckable(True)
            self._admin_btn.setChecked(True)
            self._admin_btn.setFixedHeight(36)

            self._general_btn = QPushButton("General")
            self._general_btn.setObjectName("typeBtn")
            self._general_btn.setCheckable(True)
            self._general_btn.setFixedHeight(36)

            self._type_group = QButtonGroup(self)
            self._type_group.setExclusive(True)
            self._type_group.addButton(self._admin_btn)
            self._type_group.addButton(self._general_btn)

            type_row.addWidget(self._admin_btn)
            type_row.addWidget(self._general_btn)
            cl.addLayout(type_row)

            # First account is always Admin
            self._admin_btn.setEnabled(False)
            self._general_btn.setEnabled(False)

            note = QLabel("First account is always Administrator")
            note.setStyleSheet(
                "font-size:11px;color:#45475a;background:transparent;"
            )
            cl.addSpacing(5)
            cl.addWidget(note)

        # ── Error bar ──
        cl.addSpacing(12)
        self._error_frame = QFrame()
        self._error_frame.setObjectName("errorBox")
        self._error_frame.setFixedHeight(36)
        self._error_frame.setVisible(False)
        err_row = QHBoxLayout(self._error_frame)
        err_row.setContentsMargins(12, 0, 12, 0)
        err_row.setSpacing(8)
        err_icon = QLabel("⚠")
        err_icon.setStyleSheet(
            "font-size:13px;color:#f38ba8;background:transparent;border:none;"
        )
        err_row.addWidget(err_icon)
        self._error_text = QLabel()
        self._error_text.setStyleSheet(
            "font-size:12px;color:#f38ba8;background:transparent;border:none;"
        )
        err_row.addWidget(self._error_text, 1)
        cl.addWidget(self._error_frame)

        # ── Submit button ──
        cl.addSpacing(14)
        btn_text = "Create Account" if self._setup_mode else "Sign In"
        self._submit_btn = QPushButton(btn_text)
        self._submit_btn.setObjectName("loginSubmitBtn")
        self._submit_btn.setFixedHeight(46)
        self._submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._submit_btn.clicked.connect(self._on_submit)
        cl.addWidget(self._submit_btn)

        # Keyboard navigation
        self._username.input.returnPressed.connect(
            lambda: self._password.input.setFocus()
        )
        self._password.input.returnPressed.connect(self._on_submit)
        self._username.input.setFocus()

    # ------------------------------------------------------------------ #

    @staticmethod
    def _cap_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "font-size:10px;font-weight:bold;color:#6c7086;"
            "letter-spacing:1.5px;background:transparent;"
        )
        return lbl

    def _show_error(self, msg: str) -> None:
        self._error_text.setText(msg)
        self._error_frame.setVisible(True)

    def _hide_error(self) -> None:
        self._error_frame.setVisible(False)

    # ------------------------------------------------------------------ #

    def _on_submit(self) -> None:
        username = self._username.text()
        password = self._password.text()

        if not username or not password:
            self._show_error("Username and password are required.")
            return

        if self._setup_mode:
            confirm = self._confirm.text()
            if len(password) < 6:
                self._show_error("Password must be at least 6 characters.")
                return
            if password != confirm:
                self._show_error("Passwords do not match.")
                return
            self._hide_error()
            role = "Admin" if self._admin_btn.isChecked() else "General"
            auth_manager.save_credentials(username, password, role)
            self.accept()
        else:
            if auth_manager.verify_credentials(username, password):
                self._hide_error()
                self.accept()
            else:
                self._show_error("Invalid username or password.")
                self._password.clear()
                self._password.setFocus()
