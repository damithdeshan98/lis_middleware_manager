from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

import auth_manager
from add_user_dialog import AddUserDialog


class UserManagerDialog(QDialog):
    def __init__(self, current_username: str, parent=None):
        super().__init__(parent)
        self._current_username = current_username
        self.setWindowTitle("User Management")
        self.setFixedSize(500, 440)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        # Keep the app theme (not the deep-dark login background)
        self.setStyleSheet("QDialog { background-color: #3a3a3a; }")
        self._build_ui()
        self._refresh()

    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top header bar ──
        hdr = QFrame()
        hdr.setObjectName("umHeader")
        hdr.setFixedHeight(54)
        hdr_l = QHBoxLayout(hdr)
        hdr_l.setContentsMargins(20, 0, 16, 0)
        hdr_l.setSpacing(10)

        title = QLabel("User Management")
        title.setStyleSheet("font-size:15px;font-weight:bold;color:#cdd6f4;background:transparent;")
        hdr_l.addWidget(title)
        hdr_l.addStretch()

        add_btn = QPushButton("+ Add User")
        add_btn.setObjectName("addUserBtn")
        add_btn.setFixedHeight(32)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._on_add)
        hdr_l.addWidget(add_btn)
        root.addWidget(hdr)

        # ── Divider ──
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background:#5a5a5a;border:none;")
        root.addWidget(div)

        # ── Column headers ──
        col_hdr = QFrame()
        col_hdr.setFixedHeight(32)
        col_hdr.setStyleSheet("background:#424242;border:none;")
        col_l = QHBoxLayout(col_hdr)
        col_l.setContentsMargins(68, 0, 130, 0)
        col_l.setSpacing(0)

        for text, stretch in [("USERNAME", 1), ("ROLE", 0)]:
            lbl = QLabel(text)
            lbl.setStyleSheet(
                "font-size:10px;font-weight:bold;color:#6c7086;"
                "letter-spacing:1.2px;background:transparent;"
            )
            col_l.addWidget(lbl, stretch)
        root.addWidget(col_hdr)

        # ── Scrollable user list ──
        self._list_container = QWidget()
        self._list_container.setObjectName("umList")
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)
        self._list_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(self._list_container)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        root.addWidget(scroll, 1)

        # ── Footer ──
        footer = QFrame()
        footer.setFixedHeight(52)
        footer.setStyleSheet("background:#424242;border-top:1px solid #5a5a5a;")
        foot_l = QHBoxLayout(footer)
        foot_l.setContentsMargins(16, 0, 16, 0)

        self._count_lbl = QLabel()
        self._count_lbl.setStyleSheet("font-size:12px;color:#6c7086;background:transparent;")
        foot_l.addWidget(self._count_lbl)
        foot_l.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(34)
        close_btn.setFixedWidth(80)
        close_btn.clicked.connect(self.accept)
        foot_l.addWidget(close_btn)
        root.addWidget(footer)

    # ------------------------------------------------------------------ #

    def _refresh(self) -> None:
        # Remove all existing rows (preserve the trailing stretch)
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        users = auth_manager.list_users()
        self._count_lbl.setText(f"{len(users)} user{'s' if len(users) != 1 else ''}")

        if not users:
            empty = QLabel("No users found.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color:#6c7086;font-size:13px;background:transparent;")
            self._list_layout.insertWidget(0, empty)
            return

        for i, user in enumerate(users):
            row = self._make_row(user["username"], user["role"], i)
            self._list_layout.insertWidget(i, row)

    def _make_row(self, username: str, role: str, index: int) -> QFrame:
        row = QFrame()
        row.setObjectName("userRow")
        row.setFixedHeight(58)
        row.setStyleSheet(
            "QFrame#userRow { background-color: #3a3a3a; border-bottom: 1px solid #4a4a4a; }"
            "QFrame#userRow:hover { background-color: #424242; }"
        )
        row_l = QHBoxLayout(row)
        row_l.setContentsMargins(16, 0, 12, 0)
        row_l.setSpacing(12)

        # ── Avatar circle ──
        avatar = QLabel(username[0].upper())
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        colors = ["#89b4fa", "#a6e3a1", "#fab387", "#f38ba8", "#cba6f7"]
        color = colors[index % len(colors)]
        avatar.setStyleSheet(
            f"background:{color};border-radius:18px;"
            f"color:#1e1e2e;font-weight:bold;font-size:15px;border:none;"
        )
        row_l.addWidget(avatar)

        # ── Username + "You" badge ──
        name_col = QHBoxLayout()
        name_col.setSpacing(8)
        name_col.setContentsMargins(0, 0, 0, 0)

        name_lbl = QLabel(username)
        name_lbl.setStyleSheet(
            "font-size:13px;font-weight:bold;color:#cdd6f4;background:transparent;"
        )
        name_col.addWidget(name_lbl)

        if username == self._current_username:
            you = QLabel("You")
            you.setStyleSheet(
                "font-size:10px;color:#89b4fa;"
                "background:rgba(137,180,250,0.12);"
                "border:1px solid rgba(137,180,250,0.3);"
                "border-radius:4px;padding:1px 6px;"
            )
            name_col.addWidget(you)

        name_col.addStretch()
        row_l.addLayout(name_col, 1)

        # ── Role chip ──
        role_color = "#89b4fa" if role == "Admin" else "#a6e3a1"
        role_bg    = "rgba(137,180,250,0.10)" if role == "Admin" else "rgba(166,227,161,0.10)"
        role_lbl = QLabel(role)
        role_lbl.setFixedWidth(72)
        role_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        role_lbl.setStyleSheet(
            f"font-size:11px;font-weight:bold;color:{role_color};"
            f"background:{role_bg};border-radius:5px;padding:3px 8px;border:none;"
        )
        row_l.addWidget(role_lbl)

        # ── Remove button ──
        rm = QPushButton("Remove")
        rm.setObjectName("removeUserBtn")
        rm.setFixedHeight(28)
        rm.setFixedWidth(72)
        if username == self._current_username:
            rm.setEnabled(False)
            rm.setToolTip("Cannot remove your own account")
        else:
            rm.setCursor(Qt.CursorShape.PointingHandCursor)
            rm.clicked.connect(lambda checked, u=username: self._on_remove(u))
        row_l.addWidget(rm)

        return row

    # ------------------------------------------------------------------ #

    def _on_add(self) -> None:
        dlg = AddUserDialog(parent=self)
        if dlg.exec() == AddUserDialog.DialogCode.Accepted:
            self._refresh()

    def _on_remove(self, username: str) -> None:
        reply = QMessageBox.warning(
            self,
            "Remove User",
            f"Are you sure you want to remove the account <b>{username}</b>?<br>"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            auth_manager.remove_user(username)
            self._refresh()
