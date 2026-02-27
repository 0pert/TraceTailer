import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from src.ttail.main_window import MainWindow
from src.ttail.app_config import AppConfig


def main():
    app = QApplication(sys.argv)
    settings = AppConfig()
    app.setWindowIcon(QIcon(str(settings.tracetailer_icon)))
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
