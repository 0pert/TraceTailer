from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QFileDialog,
    QPlainTextEdit,
)
from PyQt6.QtGui import (
    QAction,
    QFont
)
from pathlib import Path

from src.ttail.highlighter import HighLighter
from src.ttail.toolbar import ToolBar
from src.ttail.dialog_windows import AboutDialog, SettingsDialog
from src.ttail.app_config import AppConfig
from src.ttail.settings import FILE_DIALOG_DIR, FILTER


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.filename = ""
        self.is_loading = False

        self.settings = AppConfig()

        self.setWindowTitle("TraceTailer")
        self.setMinimumSize(QSize(1200, 600))
        # self.setWindowIcon(QIcon('img/icon.png'))

        self.content = QPlainTextEdit()
        self.content.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.highlighter = HighLighter(self.content.document())
        self.setCentralWidget(self.content)

        self.set_font(self.settings.load_font_settings())

        # Top menu
        self.menu = self.menuBar()
        file_menu = self.menu.addMenu("&File")

        button_action = QAction("📃 New", self)
        button_action.setStatusTip("Create new file")
        button_action.setShortcut("Ctrl+N")
        button_action.triggered.connect(self.new_file)
        file_menu.addAction(button_action)

        button_action = QAction("📂 Open", self)
        button_action.setStatusTip("Open existing file...")
        button_action.setShortcut("Ctrl+O")
        button_action.triggered.connect(self.open_file)
        file_menu.addAction(button_action)

        button_action = QAction("💾 Save", self)
        button_action.setStatusTip("Save file")
        button_action.setShortcut("Ctrl+S")
        button_action.triggered.connect(self.save_file)
        file_menu.addAction(button_action)

        button_action = QAction("💾 Save as", self)
        button_action.setStatusTip("Save as new file")
        button_action.setShortcut("Ctrl+Shift+S")
        button_action.triggered.connect(self.save_as)
        file_menu.addAction(button_action)

        button_action = QAction("⚙️ Settings", self)
        # button_action.setStatusTip("Save as new file")
        # button_action.setShortcut("Ctrl+Shift+S")
        button_action.triggered.connect(self.show_settings)
        file_menu.addAction(button_action)

        help_menu = self.menu.addMenu("&Help")

        # button_action = QAction("❔ Help", self)
        # button_action.triggered.connect(self.help)
        # help_menu.addAction(button_action)

        button_action = QAction("ℹ️ About", self)
        button_action.triggered.connect(self.about)
        help_menu.addAction(button_action)

        self.setStatusBar(QStatusBar(self))

        self.toolbar = ToolBar()
        self.toolbar.open_btn.clicked.connect(self.open_file)
        self.toolbar.profile_changed.connect(self.on_profile_changed)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.toolbar)

        # Timer for debouncing
        self.profile_timer = QTimer()
        self.profile_timer.setSingleShot(True)
        self.profile_timer.timeout.connect(self.do_rehighlight)

        self.content.cursorPositionChanged.connect(self.update_info)
        self.update_info()

    def set_font(self, info: list=None):
        current_settings = self.settings.load_font_settings()
        font = QFont(current_settings[0], current_settings[1])
        if info:
            font = QFont(info[0], info[1])   
 
        self.content.setFont(font)

    #### File handling functions
    def new_file(self):
        self.content.setPlainText("")
        self.filename = ""

    def open_file(self):
        filename, filter = QFileDialog.getOpenFileName(
            parent=None,
            caption="Open File",
            directory=FILE_DIALOG_DIR,
            filter=FILTER,
        )
        if filename:
            self.filename = filename
            self.is_loading = True
            self.highlighter.setDocument(None)
            self.statusBar().showMessage("Loading file......")
            with open(Path(self.filename), "r", encoding="UTF-8") as f:
                data = f.read()

            self.content.setPlainText(data)

            QTimer.singleShot(100, self.reattach_highlighter)
            self.update_info()

    def save_file(self):
        if self.filename:
            data = self.content.toPlainText()
            with open(self.filename, "w", encoding="UTF-8") as f:
                f.write(data)
        else:
            self.save_as()

    def save_as(self):
        filename, filter = QFileDialog.getSaveFileName(
            parent=None,
            caption="Save File",
            directory=FILE_DIALOG_DIR,
            filter=FILTER,
        )
        if filename:
            with open(Path(filename), "w", encoding="UTF-8") as f:
                f.write(self.content.toPlainText())

    def about(self):
        about = AboutDialog(self)
        about.exec()

    def show_settings(self):
        settings = SettingsDialog(self)
        settings.exec()

    #### Highligtning functions
    def on_profile_changed(self, profile_name):
        """Update highlighting when profile changing"""
        rules = self.toolbar.get_current_rules()
        self.highlighter.update(rules)

        # Short delay to change more rules at once
        self.profile_timer.stop()
        self.profile_timer.start(1000)

    def do_rehighlight(self):
        """Actual rehighlight after delay"""
        self.statusBar().showMessage("Updating highlighting...")
        QTimer.singleShot(10, self.finish_rehighlight)

    def finish_rehighlight(self):
        self.highlighter.rehighlight()
        self.statusBar().showMessage("Finished!", 1000)

    def reattach_highlighter(self):
        """Reattach highlighter after opening file"""
        self.highlighter.setDocument(self.content.document())
        self.is_loading = False

        # Show number of rows
        line_count = self.content.document().blockCount()
        if line_count > self.highlighter.max_blocks:
            self.statusBar().showMessage(
                f"File loaded ({line_count:,} rows). "
                f"Highlighting limit set to first {self.highlighter.max_blocks:,} rows.",
                5000,
            )
        else:
            self.statusBar().showMessage(f"File loaded ({line_count:,} rows)", 2000)

    def update_info(self):
        cursor_position = self.content.textCursor()
        line = cursor_position.blockNumber() + 1
        column = cursor_position.columnNumber() + 1
        total_lines = self.content.document().blockCount()

        info = f"File: {self.filename}\nRow: {line}/{total_lines} | Column: {column}"
        self.toolbar.info.setText(info)
