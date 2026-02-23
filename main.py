import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from src.ttail.main_window import MainWindow
from src.ttail.settings import ICON


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(ICON)))
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
