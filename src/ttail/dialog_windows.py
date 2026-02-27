from PyQt6.QtWidgets import (
    QDialog,
    QSpinBox,
    QFontComboBox,
    QDialogButtonBox,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt

from src.ttail.settings import PICTURE
from src.ttail.color import Color


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("About")

        QBtn = (
            QDialogButtonBox.StandardButton.Ok  # | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        # self.buttonBox.   rejected.connect(self.reject)

        layout = QVBoxLayout()
        label = QLabel()
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setText(f"""
    <img src="{PICTURE}" alt="TraceTailer logo" width="200" height="200"><br>
    <span style='font-size: 9pt;'>v0.2.2</span><br><br>
    <span style='font-size: 11pt;'>Kontakt: <a href='mailto:oliver@bytesofit.se'>oliver@bytesofit.se</a><br>
    GitHub: <a href='https://github.com/0pert/TraceTailer.git'>github.com/Opert/TraceTailer</a><br><br>
    © 2026 Oliver Broman<br></span>
    <span style='font-size: 9pt;'>Built with Python 3.14 and PyQt6<br></span>
""")

        label.setOpenExternalLinks(True)

        layout.addWidget(label)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Settings")

        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        current_font_settings = self.parent.settings.load_font_settings()
        current_style_settings = self.parent.settings.load_style_settings()
        layout = QVBoxLayout()

        # -- Font settings -----------------------------------------
        font_group = QGroupBox("Font")
        font_layout = QHBoxLayout()

        self.combobox = QFontComboBox()
        self.combobox.setCurrentText(current_font_settings[0])
        self.combobox.currentFontChanged.connect(self.on_change)
        font_layout.addWidget(self.combobox)

        font_layout.addWidget(QLabel("Size:"))
        self.font_size = QSpinBox()
        self.font_size.setValue(current_font_settings[1])
        self.font_size.valueChanged.connect(self.on_change)
        font_layout.addWidget(self.font_size)

        font_group.setLayout(font_layout)

        # -- Style settings -----------------------------------------
        style_group = QGroupBox("Style")
        style_layout = QVBoxLayout()

        style_layout.addWidget(QLabel("Background color:"))
        self.bg_color = Color()
        style_layout.addLayout(self.bg_color.color_layout)
        self.bg_color.color_edit.setText(current_style_settings[1])
        self.bg_color.update_color_preview(current_style_settings[1])
        self.bg_color.color_edit.textChanged.connect(self.on_change)

        style_layout.addWidget(QLabel("Text color:"))
        self.text_color = Color()
        style_layout.addLayout(self.text_color.color_layout)
        self.text_color.color_edit.setText(current_style_settings[0])
        self.text_color.update_color_preview(current_style_settings[0])
        self.text_color.color_edit.textChanged.connect(self.on_change)

        style_layout.addWidget(QLabel("Standard text color:"))

        style_group.setLayout(style_layout)

        layout.addWidget(style_group)
        layout.addWidget(font_group)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def accept(self):
        self.parent.settings.save_font_settings(
            self.font_size.value(), self.combobox.currentText()
        )
        self.parent.settings.save_style_settings(
            self.text_color.color_edit.text(), self.bg_color.color_edit.text()
        )
        self.parent.set_font()
        self.parent.set_palette()
        return super().accept()

    def reject(self):
        self.parent.set_font()
        self.parent.set_palette()
        return super().reject()

    def on_change(self):
        font_info = [self.combobox.currentText(), self.font_size.value()]
        self.parent.set_font(font_info)

        style_info = [
            self.text_color.color_edit.text(),
            self.bg_color.color_edit.text(),
        ]
        self.parent.set_palette(style_info)
