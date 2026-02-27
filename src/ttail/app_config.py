from PyQt6.QtCore import QStandardPaths, QSettings
from pathlib import Path
import shutil


class AppConfig:
    ROOT_DIR = Path.cwd()
    SAVED_PROFILES = ROOT_DIR / "profile.json"
    FILE_DIALOG_DIR = ""  # "C:\\"
    FILTER = "Text Files (*.txt *.log);;All Files (*)"
    ICON = ROOT_DIR / "img/TraceTailer_icon.ico"
    PICTURE = ROOT_DIR / "img/TraceTailer.png"

    def __init__(self):
        self.settings = QSettings("BytesOfIT", "TraceTailer")

        config_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        )
        self.config_path = Path(config_dir) / "TraceTailer"
        self.config_path.mkdir(parents=True, exist_ok=True)

        if not self.SAVED_PROFILES.exists():
            shutil.copy(self.ROOT_DIR / "src/ttail/default_profile.json", self.ROOT_DIR / "profile.json")


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
