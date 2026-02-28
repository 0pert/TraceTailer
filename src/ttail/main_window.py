from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QFileDialog,
    QPlainTextEdit,
    QWidget,
    QVBoxLayout,
)
from PyQt6.QtGui import (
    QAction,
    QFont,
    QColor,
    QPalette,
)
from pathlib import Path
import os

from src.ttail.highlighter import HighLighter
from src.ttail.toolbar import ToolBar
from src.ttail.dialog_windows import AboutDialog, SettingsDialog
from src.ttail.app_config import AppConfig
from src.ttail.file_watcher import FileWatcher
from src.ttail.search_selection import SearchAndSelect


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.is_loading = False
        self.current_file_size = 0
        self.tail_mode = False
        self.auto_scroll = True

        self.searchbar_visible = False
    

        self.settings = AppConfig()

        self.setWindowTitle("TraceTailer")
        self.setMinimumSize(QSize(1200, 600))

        # -- Main Layout -------------------------------------------------
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.content = QPlainTextEdit()
        self.content.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self.highlighter = HighLighter(self.content.document())

        self.set_font(self.settings.load_font_settings())
        self.set_palette()

        # Top menu
        self.menu = self.menuBar()
        file_menu = self.menu.addMenu("&File")
        view_menu = self.menuBar().addMenu("View")
        help_menu = self.menu.addMenu("&Help")

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

        # -- Search field (hidden by defalut) --------------------------------
        self.search_widget = SearchAndSelect(self)
        layout.addWidget(self.search_widget)

        layout.addWidget(self.content)
        self.setCentralWidget(central_widget)

        find_action = QAction("Find", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.search_widget.show_search_bar)
        self.addAction(find_action)

        find_hide_action = QAction("Hide search", self)
        find_hide_action.setShortcut("ESCAPE")
        find_hide_action.triggered.connect(self.search_widget.hide_search_bar)
        self.addAction(find_hide_action)

        self.content.selectionChanged.connect(self.search_widget.on_selection_changed)

        

        # -- Tail mode -------------------------------------------------------
        # Tail mode action
        self.file_watcher = FileWatcher(self)
        self.tail_action = QAction("Tail File", self)
        self.tail_action.setShortcut("F5")
        self.tail_action.setCheckable(True)
        self.tail_action.toggled.connect(self.file_watcher.toggle_tail_mode)

        # Auto-scroll action
        self.auto_scroll_action = QAction("Auto Scroll", self)
        self.auto_scroll_action.setCheckable(True)
        self.auto_scroll_action.setChecked(True)
        self.auto_scroll_action.toggled.connect(self.file_watcher.toggle_auto_scroll)

        view_menu.addAction(self.tail_action)
        view_menu.addAction(self.auto_scroll_action)

        # self.file_watcher = QFileSystemWatcher()
        self.file_watcher.fileChanged.connect(self.file_watcher.on_file_changed)

        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.file_watcher.update_file_content)

        self.content.verticalScrollBar().valueChanged.connect(
            self.file_watcher.on_scroll
        )

    # ------------------------------------------------------------------------
    # -- Font / Style settings -----------------------------------------------
    # ------------------------------------------------------------------------
    def about(self):
        about = AboutDialog(self)
        about.exec()

    def show_settings(self):
        settings = SettingsDialog(self)
        settings.exec()

    def set_font(self, info: list = None):
        current_settings = self.settings.load_font_settings()
        font = QFont(current_settings[0], current_settings[1])
        if info:
            font = QFont(info[0], info[1])

        self.content.setFont(font)

    def set_palette(self, info: list = None):
        palette = self.content.palette()

        style = self.settings.load_style_settings()
        if info:
            style = info

        palette.setColor(QPalette.ColorRole.Text, QColor(style[0]))
        palette.setColor(QPalette.ColorRole.Base, QColor(style[1]))
        # palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        # palette.setColor(QPalette.ColorRole.Highlight, QColor("#000000"))

        self.content.setPalette(palette)

    # ------------------------------------------------------------------------
    # -- File handling functions ---------------------------------------------
    # ------------------------------------------------------------------------
    def new_file(self):
        self.content.setPlainText("")
        self.file_path = ""

    def open_file(self):
        if self.file_path:
            self.file_watcher.removePath(self.file_path)

        file_path, filter = QFileDialog.getOpenFileName(
            parent=None,
            caption="Open File",
            directory=self.settings.FILE_DIALOG_DIR,
            filter=self.settings.FILTER,
        )
        if file_path:
            self.file_path = file_path
            self.current_file_size = os.path.getsize(self.file_path)
            self.is_loading = True
            self.highlighter.setDocument(None)
            self.statusBar().showMessage("Loading file......")
            with open(Path(self.file_path), "r", encoding="UTF-8") as f:
                data = f.read()

            self.content.setPlainText(data)

            QTimer.singleShot(100, self.reattach_highlighter)
            self.update_info()

    def save_file(self):
        if self.file_path:
            data = self.content.toPlainText()
            with open(self.file_path, "w", encoding="UTF-8") as f:
                f.write(data)
        else:
            self.save_as()

    def save_as(self):
        file_path, filter = QFileDialog.getSaveFileName(
            parent=None,
            caption="Save File",
            directory=self.settings.FILE_DIALOG_DIR,
            filter=self.settings.FILTER,
        )
        if file_path:
            with open(Path(file_path), "w", encoding="UTF-8") as f:
                f.write(self.content.toPlainText())

    # ------------------------------------------------------------------------
    # -- Highligtning functions ----------------------------------------------
    # ------------------------------------------------------------------------
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

        info = f"File: {self.file_path}\nRow: {line}/{total_lines} | Column: {column}"
        self.toolbar.info.setText(info)
