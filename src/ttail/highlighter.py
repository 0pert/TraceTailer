from PyQt6.QtCore import QRegularExpression

from PyQt6.QtGui import (
    QColor,
    QSyntaxHighlighter,
    QTextCharFormat,
)
from profiles import PROFILES


class HighLighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.highlighting_rules = []
        self.max_blocks = 1000000
        self.current_block_count = 0
        # Create format for patterns
        for pattern in PROFILES["Standard"]:
            format = QTextCharFormat()
            format.setForeground(QColor(pattern["color"]))
            pattern = QRegularExpression(pattern["expression"])
            self.highlighting_rules.append((pattern, format))

    def update(self, rules):
        self.highlighting_rules = []
        for rule in rules:
            if rule["enabled"]:
                format = QTextCharFormat()
                format.setForeground(QColor(rule["color"]))
                pattern = QRegularExpression(rule["expression"])
                self.highlighting_rules.append((pattern, format))

    def highlightBlock(self, text):
        block_number = self.currentBlock().blockNumber()
        if block_number > self.max_blocks:
            return

        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)
