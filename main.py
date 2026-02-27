import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from src.ttail.main_window import MainWindow
from src.ttail.app_config import AppConfig


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(AppConfig().ICON)))
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
