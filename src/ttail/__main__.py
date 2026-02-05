import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from main_window import MainWindow



def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('img/icon.png'))
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
