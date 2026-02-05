from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QDockWidget,
    QComboBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
)
from PyQt6.QtGui import (
    QColor,
)
from profiles import PROFILES


class ToolBar(QDockWidget):
    profile_changed = pyqtSignal(str)  # Signal for profile change

    def __init__(self):
        super().__init__("⚙️ ToolBar")
        self.resize(250, self.height())

        self.open_btn = QPushButton("📂Open")
        self.open_btn.setStatusTip("Open file")

        self.dropdown_label = QLabel("Profile:")
        self.dropdown = QComboBox()
        profile_list = []
        for i, _ in PROFILES.items():
            profile_list.append(i)
        self.dropdown.addItems(profile_list)
        self.dropdown.currentTextChanged.connect(self.dropdown_choice)

        self.sidebar_list = QListWidget()
        self.dropdown_choice("Standard")
        self.sidebar_list.itemChanged.connect(self.rule_toggled)

        self.info = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.open_btn)
        layout.addWidget(self.dropdown)
        layout.addWidget(self.sidebar_list)
        layout.addWidget(self.info)

        content = QWidget()
        content.setLayout(layout)
        self.setWidget(content)

        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            # | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

    def dropdown_choice(self, text: str):
        self.sidebar_list.clear()

        for rule in PROFILES[text]:
            item = QListWidgetItem(f"● {rule['name']}")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked
                if rule.get("enabled", True)
                else Qt.CheckState.Unchecked
            )
            item.setForeground(QColor(rule["color"]))
            self.sidebar_list.addItem(item)

        # Send signal if profile changing
        try:
            self.profile_changed.emit(text)
        except Exception:
            pass

    def rule_toggled(self, item):
        """Handle rule toggle"""
        current_profile = self.dropdown.currentText()
        try:
            self.profile_changed.emit(current_profile)
        except Exception:
            pass

    def get_current_rules(self):
        """Get current rules status"""
        current_profile = self.dropdown.currentText()
        rules = []
        for idx, rule in enumerate(PROFILES[current_profile]):
            item = self.sidebar_list.item(idx)
            rule_copy = rule.copy()
            if item:
                rule_copy["enabled"] = item.checkState() == Qt.CheckState.Checked
            rules.append(rule_copy)
        # print(rules)
        return rules
