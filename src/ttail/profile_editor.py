from PyQt6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QComboBox,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QGroupBox,
    QHBoxLayout,
    QFormLayout,
    QPushButton,
    QColorDialog,
    QCheckBox,
    QMessageBox,
)
from PyQt6.QtGui import (
    QColor,
)
import json
from src.ttail.settings import SAVED_PROFILES


class ProfileEditor(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Profile Editor")
        self.setMinimumSize(800, 600)

        self.current_profile = None
        self.current_patterns = []

        layout = QVBoxLayout()

        # --- Profile ---
        profile_group = QGroupBox("Profile")
        profile_layout = QHBoxLayout()

        self.profile_dropdown = QComboBox()
        self.read_profiles()
        self.profile_dropdown.currentTextChanged.connect(self.on_profile_changed)

        profile_layout.addWidget(QLabel("Select Profile:"))
        profile_layout.addWidget(self.profile_dropdown, 1)

        self.new_profile_btn = QPushButton("New Profile")
        self.new_profile_btn.clicked.connect(self.create_new_profile)
        profile_layout.addWidget(self.new_profile_btn)

        self.delete_profile_btn = QPushButton("Delete Profile")
        self.delete_profile_btn.clicked.connect(self.delete_current_profile)
        profile_layout.addWidget(self.delete_profile_btn)

        profile_group.setLayout(profile_layout)
        layout.addWidget(profile_group)

        main_layout = QHBoxLayout()

        # --- Pattern list ---
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Patterns:"))

        self.pattern_list = QListWidget()
        self.pattern_list.currentRowChanged.connect(self.on_pattern_selected)
        left_layout.addWidget(self.pattern_list)

        list_buttons = QHBoxLayout()
        self.add_pattern_btn = QPushButton("Add Pattern")
        self.add_pattern_btn.clicked.connect(self.add_new_pattern)
        self.remove_pattern_btn = QPushButton("Remove Pattern")
        self.remove_pattern_btn.clicked.connect(self.remove_current_pattern)
        list_buttons.addWidget(self.add_pattern_btn)
        list_buttons.addWidget(self.remove_pattern_btn)
        left_layout.addLayout(list_buttons)

        main_layout.addLayout(left_layout, 1)

        # --- Detail information ---
        right_group = QGroupBox("Details")
        right_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self.on_detail_changed)
        right_layout.addRow("Name:", self.name_edit)

        self.expression_edit = QLineEdit()
        self.expression_edit.textChanged.connect(self.on_detail_changed)
        right_layout.addRow("Regex:", self.expression_edit)

        # --- Color choice ---
        color_layout = QHBoxLayout()
        self.color_edit = QLineEdit()
        self.color_edit.textChanged.connect(self.on_detail_changed)
        self.color_preview = QLabel("    ")
        self.color_preview.setStyleSheet("border: 1px solid black;")
        self.color_preview.setFixedSize(30, 20)
        self.color_btn = QPushButton("Choose...")
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_edit, 1)
        color_layout.addWidget(self.color_preview)
        color_layout.addWidget(self.color_btn)
        right_layout.addRow("Color:", color_layout)

        self.bold_checkbox = QCheckBox("Bold")
        self.bold_checkbox.stateChanged.connect(self.on_detail_changed)
        right_layout.addRow("", self.bold_checkbox)

        self.enabled_checkbox = QCheckBox("Enabled by default")
        self.enabled_checkbox.stateChanged.connect(self.on_detail_changed)
        right_layout.addRow("", self.enabled_checkbox)

        right_group.setLayout(right_layout)
        main_layout.addWidget(right_group, 1)

        layout.addLayout(main_layout)

        # --- Bottom ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_all)
        button_layout.addWidget(self.save_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)

        self.on_profile_changed(self.profile_list[0])
        self.setLayout(layout)

    def read_profiles(self):
        self.profile_dropdown.clear()
        self.profiles = Profiles()
        self.profile_list = []
        for i, _ in self.profiles.profiles.items():
            self.profile_list.append(i)
        self.profile_dropdown.addItems(self.profile_list)

    def on_detail_changed(self):
        current_row = self.pattern_list.currentRow()
        if current_row < 0:
            return

        pattern = self.current_patterns[current_row]
        pattern["name"] = self.name_edit.text()
        pattern["expression"] = self.expression_edit.text()
        pattern["color"] = self.color_edit.text()
        pattern["bold"] = self.bold_checkbox.isChecked()
        pattern["enabled"] = self.enabled_checkbox.isChecked()

        item = self.pattern_list.item(current_row)
        item.setText(pattern["name"])
        item.setForeground(QColor(pattern["color"]))

        self.update_color_preview(pattern["color"])

    def save_all(self):
        # print(self.profiles.profiles)
        self.profiles.save_profiles()
        QMessageBox.information(self, "Saved", "Profile saved successfully!")

    def on_profile_changed(self, profile_name):

        if not profile_name:
            return

        self.current_profile = profile_name
        self.current_patterns = self.profiles.profiles[profile_name]
        self.refresh_pattern_list()

    def refresh_pattern_list(self):
        self.pattern_list.clear()

        for pattern in self.current_patterns:
            item = QListWidgetItem(pattern["name"])

            # Sätt färg på listan för att visa mönstrets färg
            color = QColor(pattern["color"])
            item.setForeground(color)

            self.pattern_list.addItem(item)

        if self.current_patterns:
            self.pattern_list.setCurrentRow(0)

    def on_pattern_selected(self, row):

        if row < 0 or row >= len(self.current_patterns):
            self.name_edit.clear()
            self.expression_edit.clear()
            self.color_edit.clear()
            self.bold_checkbox.setChecked(False)
            self.enabled_checkbox.setChecked(True)
            return

        pattern = self.current_patterns[row]

        self.name_edit.blockSignals(True)
        self.expression_edit.blockSignals(True)
        self.color_edit.blockSignals(True)
        self.bold_checkbox.blockSignals(True)
        self.enabled_checkbox.blockSignals(True)

        self.name_edit.setText(pattern["name"])
        self.expression_edit.setText(pattern["expression"])
        self.color_edit.setText(pattern["color"])
        self.update_color_preview(pattern["color"])
        self.bold_checkbox.setChecked(pattern.get("bold", False))
        self.enabled_checkbox.setChecked(pattern.get("enabled", True))

        self.name_edit.blockSignals(False)
        self.expression_edit.blockSignals(False)
        self.color_edit.blockSignals(False)
        self.bold_checkbox.blockSignals(False)
        self.enabled_checkbox.blockSignals(False)

    def create_new_profile(self):
        from PyQt6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self, "New Profile", "Profile name:")

        if ok and name:
            self.profiles.profiles[name] = []
            self.profiles.save_profiles()
            self.read_profiles()
            self.profile_dropdown.setCurrentText(name)

    def delete_current_profile(self):
        if not self.current_profile:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete profile '{self.current_profile}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            del self.profiles.profiles[self.current_profile]
            self.profiles.save_profiles()
            self.read_profiles()

    def add_new_pattern(self):
        new_pattern = {
            "name": "New Pattern",
            "expression": r".*",
            "color": "#FFFFFF",
            "bold": False,
            "enabled": True,
        }

        self.current_patterns.append(new_pattern)
        self.refresh_pattern_list()
        self.pattern_list.setCurrentRow(len(self.current_patterns) - 1)

    def remove_current_pattern(self):
        current_row = self.pattern_list.currentRow()
        if current_row < 0:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete pattern '{self.current_patterns[current_row]['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            del self.current_patterns[current_row]
            self.refresh_pattern_list()

    def choose_color(self):
        """Öppna färgväljare"""
        current_color = QColor(self.color_edit.text())
        color = QColorDialog.getColor(current_color, self, "Choose Color")

        if color.isValid():
            self.color_edit.setText(color.name())
            self.update_color_preview(color.name())

    def update_color_preview(self, color_hex):
        """Uppdatera färgförhandsvisning"""
        self.color_preview.setStyleSheet(
            f"background-color: {color_hex}; border: 1px solid black;"
        )


class Profiles:
    def __init__(self):
        self.profiles = self.load_profiles()

    def get_profile(self, profile):
        return self.profiles[profile]

    def load_profiles(self):
        with open("profile.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def save_profiles(self):
        with open("profile.json", "w", encoding="utf-8") as f:
            json.dump(self.profiles, f, indent=2, ensure_ascii=False)
