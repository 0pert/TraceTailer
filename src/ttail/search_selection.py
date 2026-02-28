from PyQt6.QtCore import QRegularExpression
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QTextEdit,
)
from PyQt6.QtGui import (
    QTextDocument,
    QTextCursor,
    QTextCharFormat,
    QColor,
)
import re

class SearchAndSelect(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.search_highlights = []
        self.current_search_text = ""

        self.layout = QHBoxLayout()
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

        self.layout.addWidget(QLabel("Find:"))
        self.layout.addWidget(self.search_edit)
        self.layout.addWidget(find_prev_btn)
        self.layout.addWidget(find_next_btn)
        self.layout.addWidget(close_search_btn)

        self.setObjectName("search_widget")
        self.setStyleSheet("""
    QWidget#search_widget {
        color: #ffffff;
        background-color: #242424;
        border-radius: 15%;
    }
""")
        self.setLayout(self.layout)
        self.hide()
    
    def show_search_bar(self):
        self.show()
        self.search_edit.setFocus()
        self.search_edit.selectAll()
        self.highlight_all_matches(self.current_search_text)
        self.parent.searchbar_visible = True

    def hide_search_bar(self):
        self.hide()
        self.parent.content.setFocus()
        self.clear_highlights()
        self.parent.searchbar_visible = False

    def quick_find_next(self):
        search_text = self.search_edit.text()
        if search_text:
            cursor = self.parent.content.textCursor()
            found = self.parent.content.find(search_text)
            if not found:
                # Wrap around
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                self.parent.content.setTextCursor(cursor)
                self.parent.content.find(search_text)

    def quick_find_prev(self):
        search_text = self.search_edit.text()
        if search_text:
            cursor = self.parent.content.textCursor()
            found = self.parent.content.find(search_text, QTextDocument.FindFlag.FindBackward)
            if not found:
                # Wrap around
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.parent.content.setTextCursor(cursor)
                self.parent.content.find(search_text, QTextDocument.FindFlag.FindBackward)

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
        cursor = QTextCursor(self.parent.content.document())
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        match_count = 0
        while True:
            cursor = self.parent.content.document().find(text, cursor)
            if cursor.isNull():
                break

            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format = highlight_format
            self.search_highlights.append(selection)
            match_count += 1

        # Apply highlights
        self.parent.content.setExtraSelections(self.search_highlights)

    def clear_highlights(self):
        """Clear all highlights"""
        self.search_highlights.clear()
        self.parent.content.setExtraSelections([])
        # self.current_search_text = ""

    def on_selection_changed(self):
        """When user select a word"""

        # Not when search is active #
        if self.parent.searchbar_visible:
            return

        cursor = self.parent.content.textCursor()
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
        original_cursor = self.parent.content.textCursor()
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
        cursor = QTextCursor(self.parent.content.document())
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        while True:
            cursor = self.parent.content.document().find(
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

        self.parent.content.setExtraSelections(self.search_highlights)