from pathlib import Path
import shutil

# BASE_NAME = __package__.split(".")[0]
ROOT_DIR = Path.cwd()  # / BASE_NAME

SAVED_PROFILES = ROOT_DIR / "profile.json"
if not SAVED_PROFILES.exists():
    shutil.copy(ROOT_DIR / "src/ttail/default_profile.json", ROOT_DIR / "profile.json")


FILTER = "Text Files (*.txt *.log);;All Files (*)"
FILE_DIALOG_DIR = ""  # "C:\\"

ICON = ROOT_DIR / "img/TraceTailer_icon.ico"
PICTURE = ROOT_DIR / "img/TraceTailer.png"


if __name__ == "__main__":
    # print(SAVED_PROFILES.exists())
    pass
