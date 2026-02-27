from PyQt6.QtCore import QStandardPaths, QSettings
from pathlib import Path


class AppConfig:
    def __init__(self):
        self.settings = QSettings("BytesOfIT", "TraceTailer")

        config_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        )
        self.config_path = Path(config_dir) / "TraceTailer"
        self.config_path.mkdir(parents=True, exist_ok=True)

    def save_font_settings(self, font_size, font_name):
        self.settings.setValue("font-size", font_size)
        self.settings.setValue("font-name", font_name)

    def load_font_settings(self):
        return [
            self.settings.value("font-name", "Consolas"),
            self.settings.value("font-size", 10),
        ]

    def save_style_settings(self, text_color, bg_color):
        self.settings.setValue("text-color", text_color)
        self.settings.setValue("bg-color", bg_color)

    def load_style_settings(self):
        return [
            self.settings.value("text-color", "#ffffff"),
            self.settings.value("bg-color", "#2d2d2d"),
        ]
