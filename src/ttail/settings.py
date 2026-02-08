from pathlib import Path

BASE_NAME = __package__.split(".")[0]
ROOT_DIR = Path.cwd()# / BASE_NAME

SAVED_PROFILES = ROOT_DIR / "profile.json"

FILTER = "Text Files (*.txt *.log);;All Files (*)"
FILE_DIALOG_DIR = ""#"C:\\"

ICON = ROOT_DIR / "img/TraceTailer_icon.ico"
PICTURE = ROOT_DIR / "img/TraceTailer.png"
