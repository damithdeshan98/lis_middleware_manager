import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

import auth_manager
from icon import create_app_icon
from login_dialog import LoginDialog
from main_window import MainWindow
from styles import STYLESHEET


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("LIS Middleware Manager")
    app.setApplicationDisplayName("LIS Middleware Manager")
    app.setStyleSheet(STYLESHEET)
    app.setFont(QFont("Segoe UI", 10))

    icon = create_app_icon()
    app.setWindowIcon(icon)

    login = LoginDialog()
    login.setWindowIcon(icon)
    if login.exec() != LoginDialog.DialogCode.Accepted:
        sys.exit(0)

    username, role = auth_manager.get_current_user()
    window = MainWindow(username=username, role=role)
    window.setWindowIcon(icon)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
