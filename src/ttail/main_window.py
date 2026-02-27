from PyQt6.QtCore import QSize, Qt, QTimer, QRegularExpression
from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QFileDialog,
    QPlainTextEdit,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QTextEdit,
)
from PyQt6.QtGui import (
    QAction,
    QFont,
    QTextDocument,
    QTextCursor,
    QTextCharFormat,
    QColor,
    QPalette,
)
from pathlib import Path
import re

from src.ttail.highlighter import HighLighter
from src.ttail.toolbar import ToolBar
from src.ttail.dialog_windows import AboutDialog, SettingsDialog
from src.ttail.app_config import AppConfig


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.filename = ""
        self.is_loading = False

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

        # -- Search field (hidden by defalut) --------------------------------
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search...")
        self.search_edit.returnPressed.connect(self.quick_find_next)
        self.search_edit.textChanged.connect(self.highlight_all_matches)

        find_next_btn = QPushButton("Next")
        find_next_btn.clicked.connect(self.quick_find_next)

        find_prev_btn = QPushButton("Previous")
        find_prev_btn.clicked.connect(self.quick_find_prev)

        close_search_btn = QPushButton("✕")
        close_search_btn.setMaximumWidth(30)
        close_search_btn.clicked.connect(self.hide_search_bar)

        search_layout.addWidget(QLabel("Find:"))
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(find_prev_btn)
        search_layout.addWidget(find_next_btn)
        search_layout.addWidget(close_search_btn)

        self.search_widget = QWidget()
        self.search_widget.setObjectName("search_widget")
        self.search_widget.setStyleSheet("""
    QWidget#search_widget {
        color: #ffffff;
        background-color: #242424;
        border-radius: 15%;
    }
""")
        # self.search_widget.setStyleSheet("color: #ffffff; background-color: #1b1b1b; border-radius: 15%;")
        self.search_widget.setLayout(search_layout)
        self.search_widget.hide()

        layout.addWidget(self.search_widget)

        layout.addWidget(self.content)
        self.setCentralWidget(central_widget)

        find_action = QAction("Find", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_search_bar)
        self.addAction(find_action)

        find_hide_action = QAction("Hide search", self)
        find_hide_action.setShortcut("ESCAPE")
        find_hide_action.triggered.connect(self.hide_search_bar)
        self.addAction(find_hide_action)

        self.content.selectionChanged.connect(self.on_selection_changed)

        self.searchbar_visible = False
        self.search_highlights = []
        self.current_search_text = ""

    # ------------------------------------------------------------------------
    # -- Search functions ----------------------------------------------------
    # ------------------------------------------------------------------------
    def show_search_bar(self):
        self.search_widget.show()
        self.search_edit.setFocus()
        self.search_edit.selectAll()
        self.highlight_all_matches(self.current_search_text)
        self.searchbar_visible = True

    def hide_search_bar(self):
        self.search_widget.hide()
        self.content.setFocus()
        self.clear_highlights()
        self.searchbar_visible = False

    def quick_find_next(self):
        search_text = self.search_edit.text()
        if search_text:
            cursor = self.content.textCursor()
            found = self.content.find(search_text)
            if not found:
                # Wrap around
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                self.content.setTextCursor(cursor)
                self.content.find(search_text)

    def quick_find_prev(self):
        search_text = self.search_edit.text()
        if search_text:
            cursor = self.content.textCursor()
            found = self.content.find(search_text, QTextDocument.FindFlag.FindBackward)
            if not found:
                # Wrap around
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.content.setTextCursor(cursor)
                self.content.find(search_text, QTextDocument.FindFlag.FindBackward)

    def highlight_all_matches(self, text):
        """Markera alla träffar av söktexten"""
        self.clear_highlights()

        if not text or len(text) < 2:
            self.current_search_text = ""
            return

        self.current_search_text = text

        # -- Highlight format -------------------------------------
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("#FFFF00"))
        highlight_format.setForeground(QColor("#000000"))

        # -- Find all -----------------------------------
        cursor = QTextCursor(self.content.document())
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        match_count = 0
        while True:
            cursor = self.content.document().find(text, cursor)
            if cursor.isNull():
                break

            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format = highlight_format
            self.search_highlights.append(selection)
            match_count += 1

        # Apply highlights
        self.content.setExtraSelections(self.search_highlights)

    def clear_highlights(self):
        """Clear all highlights"""
        self.search_highlights.clear()
        self.content.setExtraSelections([])
        # self.current_search_text = ""

    # ------------------------------------------------------------------------
    # -- Selection functions ----------------------------------------------------
    # ------------------------------------------------------------------------
    def on_selection_changed(self):
        """When user select a word"""

        # Not when search is active #
        if self.searchbar_visible:
            return

        cursor = self.content.textCursor()
        selected_text = cursor.selectedText()

        # Highlight relevant word
        if selected_text and len(selected_text.strip()) >= 2:
            # Check selected text
            if self.is_valid_word(selected_text):
                self.highlight_selected_word(selected_text)
            else:
                self.clear_highlights()
        else:
            self.clear_highlights()

    def is_valid_word(self, text):
        """Check if selection is a valid word highlight"""
        if text.isspace():
            return False

        # Accept word with characters, numbers and underscore
        return bool(re.match(r"^[\w\-\.]+$", text))

    def highlight_selected_word(self, word):
        """Highlight allmatching words"""
        self.search_highlights.clear()

        # Lighter highlighting for non active matchning
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("#F84E4E"))
        highlight_format.setForeground(QColor("#F8F8F8"))

        # Stronger highlighting for active marking
        current_format = QTextCharFormat()
        current_format.setBackground(QColor("#FF0000"))
        current_format.setForeground(QColor("#F8F8F8"))

        # Save current cursor
        original_cursor = self.content.textCursor()
        original_start = original_cursor.selectionStart()
        original_end = original_cursor.selectionEnd()

        # Regex for whole words only
        escaped_word = re.escape(word)
        pattern_str = r"\b" + escaped_word + r"\b"

        # case-insensitive QRegularExpression
        pattern = QRegularExpression(
            pattern_str, QRegularExpression.PatternOption.CaseInsensitiveOption
        )

        # Find all matchnings (case-sensitive)
        cursor = QTextCursor(self.content.document())
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        while True:
            cursor = self.content.document().find(
                pattern, cursor, QTextDocument.FindFlag.FindCaseSensitively
            )
            if cursor.isNull():
                break

            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor

            # Use stronger color for active selection
            if (
                cursor.selectionStart() == original_start
                and cursor.selectionEnd() == original_end
            ):
                selection.format = current_format
            else:
                selection.format = highlight_format

            self.search_highlights.append(selection)

        self.content.setExtraSelections(self.search_highlights)

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
        self.filename = ""

    def open_file(self):
        filename, filter = QFileDialog.getOpenFileName(
            parent=None,
            caption="Open File",
            directory=self.settings.FILE_DIALOG_DIR,
            filter=self.settings.FILTER,
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
            directory=self.settings.FILE_DIALOG_DIR,
            filter=self.settings.FILTER,
        )
        if filename:
            with open(Path(filename), "w", encoding="UTF-8") as f:
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

        info = f"File: {self.filename}\nRow: {line}/{total_lines} | Column: {column}"
        self.toolbar.info.setText(info)
