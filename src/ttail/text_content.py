from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPlainTextEdit, QApplication
from PyQt6.QtGui import QAction


class TextContent(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._build_actions()

    def _build_actions(self):
        self.action_undo = QAction("⬅️ Undo", self)
        self.action_undo.setShortcut("Ctrl+Z")
        self.action_undo.triggered.connect(self.undo)

        self.action_redo = QAction("➡️ Redo", self)
        self.action_redo.setShortcut("Ctrl+Y")
        self.action_redo.triggered.connect(self.redo)

        self.action_cut = QAction("✂️ Cut", self)
        self.action_cut.setShortcut("Ctrl+X")
        self.action_cut.triggered.connect(self.cut)

        self.action_copy = QAction("📋 Copy", self)
        self.action_copy.setShortcut("Ctrl+C")
        self.action_copy.triggered.connect(self.copy)

        self.action_paste = QAction("📌 Paste", self)
        self.action_paste.setShortcut("Ctrl+V")
        self.action_paste.triggered.connect(self.paste)

        self.action_copy_line = QAction("📋 Copy current line", self)
        self.action_copy_line.setShortcut("Ctrl+Shift+C")
        self.action_copy_line.triggered.connect(self.copy_current_line)

        self.action_clear = QAction("🗑️ Clear", self)
        self.action_clear.triggered.connect(self.clear)

    def get_edit_actions(self, all=False):
        if all:
            return [
                self.action_undo,
                self.action_redo,
                self.action_cut,
                self.action_copy,
                self.action_copy_line,
                self.action_paste,
                self.action_clear,
            ]
        return [self.action_copy_line, self.action_clear]

    def show_context_menu(self, pos):
        # menu = QMenu(self)
        menu = self.createStandardContextMenu()
        menu.addActions(self.get_edit_actions())
        menu.exec(self.mapToGlobal(pos))

    def copy_current_line(self):
        cursor = self.textCursor()
        cursor.select(cursor.SelectionType.LineUnderCursor)
        QApplication.clipboard().setText(cursor.selectedText())
