import os
import sys

# Đảm bảo đường dẫn module được nhận diện chuẩn xác
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication
from theme import APP_NAME
from studio import NoneCodeStudio

if __name__ == "__main__":
    app = QApplication.instance()
    if app is None:
        QApplication.setApplicationName(APP_NAME)
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setFont(QFont("Segoe UI Variable Text", 9))

    window = NoneCodeStudio()
    window.show()
    window.raise_()
    window.activateWindow()

    # Xử lý Open With từ Windows
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        if os.path.isfile(target_file):
            abs_path = os.path.abspath(target_file)
            window.set_workspace(os.path.dirname(abs_path))
            window.load_file(abs_path)
            QTimer.singleShot(400, lambda: window.toast(f"Opened: {os.path.basename(abs_path)}"))

    QTimer.singleShot(80, window.start_intro)
    sys.exit(app.exec())