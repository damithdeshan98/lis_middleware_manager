import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from icon import create_app_icon
from main_window import MainWindow
from styles import STYLESHEET


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Middleware Manager")
    app.setApplicationDisplayName("Middleware Manager")
    app.setStyleSheet(STYLESHEET)
    app.setFont(QFont("Segoe UI", 10))

    icon = create_app_icon()
    app.setWindowIcon(icon)

    window = MainWindow()
    window.setWindowIcon(icon)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
