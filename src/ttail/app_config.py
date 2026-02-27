from PyQt6.QtCore import QStandardPaths, QSettings
from pathlib import Path
import os
import sys
from src.ttail.default_profile import DEFAULT_PROFILE


class AppConfig:
    ROOT_DIR = Path.cwd()
    FILE_DIALOG_DIR = ""  # "C:\\"
    FILTER = "Text Files (*.txt *.log);;All Files (*)"

    def __init__(self):
        self.settings = QSettings("BytesOfIT", "TraceTailer")

        self.tracetailer_icon = self.resource_path("img/TraceTailer_icon.ico")
        self.tracetailer_pic = self.resource_path("img/TraceTailer.png")

        config_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        )
        self.config_path = Path(config_dir) / "TraceTailer"
        self.config_path.mkdir(parents=True, exist_ok=True)

        self.profile_file = self.config_path / "profile.json"

        if not self.profile_file.exists():
            with open(self.profile_file, "w", encoding="utf-8") as f:
                f.write(DEFAULT_PROFILE)

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

    def resource_path(self, relative_path):
        """Find the right path for .py and .exe"""
        try:
            # PyInstaller ---- _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
