STYLESHEET = """
QMainWindow {
    background-color: #404040;
}

QWidget {
    background-color: #404040;
    color: #cdd6f4;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}

QSplitter::handle {
    background-color: #5a5a5a;
    width: 1px;
}

QListWidget {
    background-color: #4a4a4a;
    border: none;
    outline: none;
    padding: 4px;
}

QListWidget::item {
    border-radius: 8px;
    margin: 2px 0;
    padding: 0;
    background-color: transparent;
}

QListWidget::item:selected {
    background-color: #5a5a5a;
}

QListWidget::item:hover:!selected {
    background-color: #525252;
}

QTextEdit {
    background-color: #2e2e2e;
    color: #cdd6f4;
    border: none;
    font-family: 'Consolas', 'Cascadia Code', 'JetBrains Mono', monospace;
    font-size: 12px;
    padding: 10px;
    selection-background-color: #666666;
}

QPushButton {
    background-color: #5a5a5a;
    color: #cdd6f4;
    border: none;
    border-radius: 6px;
    padding: 7px 16px;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #686868;
}

QPushButton:pressed {
    background-color: #767676;
}

QPushButton:disabled {
    background-color: #383838;
    color: #666666;
}

QPushButton#addBtn {
    background-color: #89b4fa;
    color: #1e1e2e;
    font-weight: bold;
    padding: 7px 18px;
}

QPushButton#addBtn:hover {
    background-color: #b4d0ff;
}

QPushButton#startAllBtn {
    background-color: #a6e3a1;
    color: #1e1e2e;
    font-weight: bold;
    padding: 7px 18px;
}

QPushButton#startAllBtn:hover {
    background-color: #c3f0c0;
}

QPushButton#stopAllBtn {
    background-color: #f38ba8;
    color: #1e1e2e;
    font-weight: bold;
    padding: 7px 18px;
}

QPushButton#stopAllBtn:hover {
    background-color: #f5a3bb;
}

QPushButton#startBtn {
    background-color: #a6e3a1;
    color: #1e1e2e;
    font-size: 14px;
    border-radius: 17px;
    padding: 0;
    font-weight: bold;
}

QPushButton#startBtn:hover {
    background-color: #c3f0c0;
}

QPushButton#startBtn:disabled {
    background-color: #2e4a2e;
    color: #666666;
}

QPushButton#stopBtn {
    background-color: #f38ba8;
    color: #1e1e2e;
    font-size: 13px;
    border-radius: 17px;
    padding: 0;
    font-weight: bold;
}

QPushButton#stopBtn:hover {
    background-color: #f5a3bb;
}

QPushButton#stopBtn:disabled {
    background-color: #4a2e35;
    color: #666666;
}

QPushButton#removeBtn {
    background-color: transparent;
    color: #585b70;
    font-size: 15px;
    border-radius: 17px;
    padding: 0;
}

QPushButton#removeBtn:hover {
    background-color: #45475a;
    color: #f38ba8;
}

QPushButton#clearLogBtn {
    background-color: transparent;
    color: #6c7086;
    border: 1px solid #313244;
    border-radius: 4px;
    padding: 3px 10px;
    font-size: 11px;
}

QPushButton#clearLogBtn:hover {
    background-color: #313244;
    color: #cdd6f4;
}

QScrollBar:vertical {
    background-color: #3a3a3a;
    width: 8px;
    border-radius: 4px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #686868;
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: #7a7a7a;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
    background: none;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background-color: #3a3a3a;
    height: 8px;
    border-radius: 4px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #686868;
    border-radius: 4px;
    min-width: 24px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #7a7a7a;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
    background: none;
}

QStatusBar {
    background-color: #4a4a4a;
    color: #9a9a9a;
    border-top: 1px solid #5a5a5a;
    font-size: 12px;
    padding: 0 8px;
}

QInputDialog {
    background-color: #4a4a4a;
}

QInputDialog QLabel {
    color: #cdd6f4;
    font-size: 13px;
}

QInputDialog QLineEdit {
    background-color: #5a5a5a;
    color: #cdd6f4;
    border: 1px solid #686868;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
}

QInputDialog QLineEdit:focus {
    border-color: #89b4fa;
}

QMessageBox {
    background-color: #4a4a4a;
}

QMessageBox QLabel {
    color: #cdd6f4;
}

QMessageBox QPushButton {
    min-width: 80px;
}
"""
