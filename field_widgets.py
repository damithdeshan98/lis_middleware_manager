"""Shared styled input field widgets used by login and add-user dialogs."""
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton

_CSS_NORMAL  = "QFrame#fieldBox{background:#16161e;border:1.5px solid #313244;border-radius:8px;}"
_CSS_FOCUSED = "QFrame#fieldBox{background:#16161e;border:1.5px solid #89b4fa;border-radius:8px;}"


def _set_placeholder(field: QLineEdit) -> None:
    pal = field.palette()
    pal.setColor(QPalette.ColorRole.PlaceholderText, QColor("#45475a"))
    field.setPalette(pal)


class TextField(QFrame):
    """Single-line text input with a left icon and focus-border highlight."""

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
        _set_placeholder(self.input)
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


class PasswordField(QFrame):
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
        _set_placeholder(self.input)
        row.addWidget(self.input, 1)

        self._eye = QPushButton("👁")
        self._eye.setObjectName("eyeBtn")
        self._eye.setFixedSize(32, 32)
        self._eye.setCheckable(True)
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
