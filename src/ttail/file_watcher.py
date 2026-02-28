from PyQt6.QtCore import QSize, Qt, QTimer, QRegularExpression, QFileSystemWatcher
import os
import sys

class FileWatcher(QFileSystemWatcher):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent

    def toggle_tail_mode(self, checked):
        """Activate/inactivate tail mode"""
        self.parent.tail_mode = checked

        if checked and self.parent.file_path:
            self.parent.file_watcher.addPath(self.parent.file_path)
            self.scroll_to_bottom()
            self.parent.statusBar().showMessage("📡 Tailing File...")
            self.parent.tail_action.setText("Tail File ✓")
        else:
            if self.parent.file_path:
                self.parent.file_watcher.removePath(self.parent.file_path)
            self.parent.statusBar().showMessage("Ready")
            self.parent.tail_action.setText("Tail File")

    def toggle_auto_scroll(self, checked):
        """Toggle auto-scroll"""
        self.parent.auto_scroll = checked

    def on_scroll(self, value):
        """Manually scrolling"""
        if not self.parent.tail_mode:
            return

        scrollbar = self.parent.content.verticalScrollBar()

        # Stop auto-scroll when user scrolling
        if value < scrollbar.maximum() - 50:
            if self.parent.auto_scroll:
                self.parent.auto_scroll = False
                self.parent.auto_scroll_action.setChecked(False)
                self.parent.statusBar().showMessage("📡 Following (auto-scroll paused)")
        else:
            # Activate auto-scroll if user scroll down to bottom
            if not self.parent.auto_scroll:
                self.parent.auto_scroll = True
                self.parent.auto_scroll_action.setChecked(True)
                self.parent.statusBar().showMessage("📡 Following file...")

    def on_file_changed(self, path):
        # Timer to avoid to many updates
        if not self.parent.update_timer.isActive():
            self.parent.update_timer.start(100)  # 100ms delay

    def scroll_to_bottom(self):
        scrollbar = self.parent.content.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_file_content(self):
        """Read new lines from file"""
        if not self.parent.file_path or not self.parent.tail_mode:
            return

        try:
            new_size = os.path.getsize(self.parent.file_path)

            if new_size > self.parent.current_file_size:
                with open(self.parent.file_path, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(self.parent.current_file_size)
                    new_content = f.read()

                if new_content:
                    # Add new lines
                    cursor = self.parent.content.textCursor()
                    cursor.movePosition(cursor.MoveOperation.End)
                    cursor.insertText(new_content)

                    # Scroll if auto-scroll acive
                    if self.parent.auto_scroll:
                        self.scroll_to_bottom()

                    # Uppdate status bar
                    new_lines = new_content.count("\n")
                    self.parent.statusBar().showMessage(
                        f"📡 Following file... (+{new_lines} lines)"
                    )

                self.parent.current_file_size = new_size

            elif new_size < self.parent.current_file_size:
                # File trunkerad - reload
                self.parent.open_file(self.parent.file_path)
                self.parent.statusBar().showMessage("📡 File reloaded (truncated)")

        except Exception as e:
            print(f"Error updating file: {e}")
            self.parent.statusBar().showMessage(f"Error: {e}")
