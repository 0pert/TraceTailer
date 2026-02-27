from PyQt6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QColorDialog,
    QPushButton,
    QLineEdit,
    QWidget,
)

from PyQt6.QtGui import QColor


class Color(QWidget):
    def __init__(self):
        super().__init__()

        self.color_layout = QHBoxLayout()
        self.color_edit = QLineEdit()

        self.color_preview = QLabel("    ")
        self.color_preview.setStyleSheet("border: 1px solid black;")
        self.color_preview.setFixedSize(30, 20)
        self.color_btn = QPushButton("Choose...")
        self.color_btn.clicked.connect(self.choose_color)

        self.color_layout.addWidget(self.color_edit, 1)
        self.color_layout.addWidget(self.color_preview)
        self.color_layout.addWidget(self.color_btn)

    def choose_color(self):
        """Open color picker"""
        current_color = QColor(self.color_edit.text())
        color = QColorDialog.getColor(current_color, self, "Choose Color")

        if color.isValid():
            self.color_edit.setText(color.name())
            self.update_color_preview(color.name())

    def update_color_preview(self, color_hex):
        """Update color preview"""
        self.color_preview.setStyleSheet(
            f"background-color: {color_hex}; border: 1px solid black;"
        )
