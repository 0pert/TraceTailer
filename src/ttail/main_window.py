from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QFileDialog,
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
from src.ttail.text_content import TextContent
from src.ttail.toolbar import ToolBar
from src.ttail.dialog_windows import AboutDialog, SettingsDialog
from src.ttail.app_config import AppConfig
from src.ttail.file_watcher import FileWatcher
from src.ttail.search_selection import SearchAndSelect
from src.ssh.ssh_dialog import SSHConnectionDialog
from src.ssh.ssh_tail import SSHTailThread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TraceTailer")
        self.setMinimumSize(QSize(1200, 600))

        self.file_path = None
        self.is_loading = False
        self.current_file_size = 0
        self.tail_mode = False
        self.auto_scroll = True

        self.file_changed = True

        self.ssh_thread = None
        self.remote_file_path = None
        self.host = None

        self.searchbar_visible = False

        self.settings = AppConfig()

        # -- Main Layout -------------------------------------------------
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.content = TextContent()
        self.content.document().setModified(False)
        self.content.document().modificationChanged.connect(self.on_text_changed)

        self.highlighter = HighLighter(self.content.document())

        self.set_font(self.settings.load_font_settings())
        self.set_palette()

        # Top menu
        self.menu = self.menuBar()
        file_menu = self.menu.addMenu("&File")
        edit_menu = self.menu.addMenu("&Edit")
        self.view_menu = self.menuBar().addMenu("&View")
        self.ssh_menu = self.menuBar().addMenu("&SSH")
        help_menu = self.menu.addMenu("&Help")

        button_action = QAction("📃 New", self)
        button_action.setShortcut("Ctrl+N")
        button_action.triggered.connect(self.new_file)
        file_menu.addAction(button_action)

        button_action = QAction("📂 Open", self)
        button_action.setShortcut("Ctrl+O")
        button_action.triggered.connect(self.open_file)
        file_menu.addAction(button_action)

        button_action = QAction("💾 Save", self)
        button_action.setShortcut("Ctrl+S")
        button_action.triggered.connect(self.save_file)
        file_menu.addAction(button_action)

        button_action = QAction("💾 Save as", self)
        button_action.setShortcut("Ctrl+Shift+S")
        button_action.triggered.connect(self.save_as)
        file_menu.addAction(button_action)

        file_menu.addSeparator()
        button_action = QAction("⚙️ Settings", self)
        button_action.triggered.connect(self.show_settings)
        file_menu.addAction(button_action)

        for action in self.content.get_edit_actions(True):
            edit_menu.addAction(action)

        button_action = QAction("ℹ️ About", self)
        button_action.triggered.connect(self.about)
        help_menu.addAction(button_action)

        self.setStatusBar(QStatusBar(self))

        self.toolbar = ToolBar(self)
        self.toolbar.open_btn.clicked.connect(self.open_file)
        self.toolbar.profile_changed.connect(self.on_profile_changed)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.toolbar)

        # Timer for debouncing
        self.profile_timer = QTimer()
        self.profile_timer.setSingleShot(True)
        self.profile_timer.timeout.connect(self.do_rehighlight)

        self.content.cursorPositionChanged.connect(self.update_info)
        self.update_info()

        self.search_widget = SearchAndSelect(self)
        layout.addWidget(self.search_widget)
        layout.addWidget(self.content)
        self.setCentralWidget(central_widget)

        self.file_watcher = FileWatcher(self)

        ssh_start = QAction("🛜 Tail Remote File (SSH)", self)
        ssh_start.triggered.connect(self.open_ssh_dialog)
        self.ssh_menu.addAction(ssh_start)
        self.ssh_stop = QAction("❌ Close connection", self.ssh_thread)
        self.ssh_stop.setEnabled(False)
        self.ssh_menu.addAction(self.ssh_stop)
        self.ssh_menu.addSeparator()
        self.sftp = QAction("📡 Read Remote File (SFTP)")
        self.sftp.triggered.connect(lambda: self.open_ssh_dialog(True))
        self.ssh_menu.addAction(self.sftp)

    def open_ssh_dialog(self, sftp=False):
        """SSH config dialog"""
        dialog = SSHConnectionDialog(self)
        if dialog.exec():
            config = dialog.get_config()
            self.connect_ssh(
                sftp,
                config["host"],
                config["username"],
                config["password"],
                config["remote_file"],
                config.get("port", 22),
            )
            self.settings.save_last_ssh(config)

    def connect_ssh(self, sftp, host, username, password, remote_file, port=22):
        """Connect and tail remote file or load remote file via sftp"""
        # Stop thread
        if self.ssh_thread and self.ssh_thread.isRunning():
            self.ssh_thread.stop()

        # Start new thread
        self.ssh_thread = SSHTailThread(
            self, host, username, password, remote_file, port
        )

        if not sftp:
            self.ssh_thread.new_content.connect(self.append_remote_content)
            self.ssh_thread.error_occurred.connect(self.show_ssh_error)
            self.ssh_thread.start()

            self.statusBar().showMessage(f"📡 Following {remote_file} on {host}")
            self.ssh_stop.triggered.connect(self.ssh_thread.stop)
            self.ssh_stop.setEnabled(True)

            self.file_watcher.tail_action.setEnabled(False)
            self.file_watcher.auto_scroll_action.setEnabled(False)

        else:
            data = self.ssh_thread.sftp()
            self.content.setPlainText(data)

        self.remote_file_path = remote_file
        self.host = host
        self.file_path = None

        self.update_info()

    def append_remote_content(self, line):
        """Add new row from remote file"""
        cursor = self.content.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(line)

        # Auto-scroll
        scrollbar = self.content.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def show_ssh_error(self, error):
        QMessageBox.critical(self, "SSH Error", f"Error: {error}")
        self.statusBar().showMessage("SSH connection failed")
        self.ssh_stop.setEnabled(False)

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
        self.file_path = None
        # self.file_changed = True
        self.remote_file_path = None
        self.file_watcher.tail_action.setEnabled(False)
        self.file_watcher.auto_scroll_action.setEnabled(False)

        self.update_info()

    def open_file(self):
        if self.file_path:
            self.file_watcher.removePath(self.file_path)

        self.file_changed = False

        file_path, filter = QFileDialog.getOpenFileName(
            parent=None,
            caption="Open File",
            directory=self.settings.FILE_DIALOG_DIR,
            filter=self.settings.FILTER,
        )
        if file_path:
            self.file_path = file_path
            self.remote_file_path = None
            self.current_file_size = os.path.getsize(self.file_path)
            self.is_loading = True
            self.file_watcher.tail_action.setEnabled(True)
            self.file_watcher.auto_scroll_action.setEnabled(True)
            self.highlighter.setDocument(None)
            self.statusBar().showMessage("Loading file...")
            with open(Path(self.file_path), "r", encoding="UTF-8") as f:
                data = f.read()

            # Make sure the content-window set to not modified
            self.content.document().blockSignals(True)
            self.content.setPlainText(data)
            self.content.document().setModified(False)
            self.content.document().blockSignals(False)
            self.file_changed = False

            QTimer.singleShot(100, self.reattach_highlighter)

            self.update_info()

    def save_file(self):
        if self.file_path:
            data = self.content.toPlainText()
            with open(self.file_path, "w", encoding="UTF-8") as f:
                f.write(data)
            self.file_changed = False
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
            self.file_changed = False
            self.file_path = file_path

    def on_text_changed(self, modified):
        if modified:
            self.file_changed = True

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
        self.statusBar().showMessage("Highlighting Updated!", 1000)

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

        if self.file_path:
            file_info = self.file_path

        elif self.remote_file_path:
            file_info = f"{self.host}:{self.remote_file_path}"

        else:
            file_info = ""

        info = f"File: {file_info}\nRow: {line}/{total_lines} | Column: {column}\nFile Saved: {not self.file_changed}"
        self.toolbar.info.setText(info)

    def closeEvent(self, event):
        """Event when program is shutting down"""
        message = "Do you want to quit?"
        if self.file_changed:
            message = "You have unsaved changes. Do you want to quit without saving?"

        reply = QMessageBox.question(
            self,
            "Close",
            message,
            QMessageBox.StandardButton.Close | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Close,
        )

        if reply == QMessageBox.StandardButton.Close:
            if self.ssh_thread and self.ssh_thread.isRunning():
                self.ssh_thread.stop()
            event.accept()
        else:
            event.ignore()
