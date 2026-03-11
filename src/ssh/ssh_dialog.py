from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QSpinBox, QDialogButtonBox, QCheckBox, QFileDialog
)

class SSHConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SSH Connection")
        self.setMinimumWidth(400)
        self.parent = parent
        
        layout = QFormLayout(self)
        
        # Host
        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("example.com")
        layout.addRow("Host:", self.host_edit)
        
        # Port
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(22)
        layout.addRow("Port:", self.port_spin)
        
        # Username
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("username")
        layout.addRow("Username:", self.username_edit)
        
        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Password:", self.password_edit)
        
        # SSH Key (optional)
        self.use_key = QCheckBox("Use SSH Key")
        self.use_key.toggled.connect(self.toggle_key_auth)
        self.use_key.setEnabled(False)
        layout.addRow("", self.use_key)
        
        self.key_path_edit = QLineEdit()
        self.key_path_edit.setEnabled(False)
        self.key_browse_btn = QPushButton("Browse...")
        self.key_browse_btn.setEnabled(False)
        self.key_browse_btn.clicked.connect(self.browse_key)
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(self.key_path_edit)
        key_layout.addWidget(self.key_browse_btn)
        layout.addRow("Key File:", key_layout)
        
        # Remote file path
        self.remote_file_edit = QLineEdit()
        self.remote_file_edit.setPlaceholderText("/var/log/application.log")
        layout.addRow("Remote File:", self.remote_file_edit)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        last_ssh = self.parent.settings.load_last_ssh()
        if last_ssh:
            self.host_edit.setText(last_ssh["host"])
            self.port_spin.setValue(last_ssh["port"])
            self.username_edit.setText(last_ssh["username"])
            self.remote_file_edit.setText(last_ssh["remote_file"])

    
    def toggle_key_auth(self, checked):
        self.password_edit.setEnabled(not checked)
        self.key_path_edit.setEnabled(checked)
        self.key_browse_btn.setEnabled(checked)
    
    def browse_key(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select SSH Key", "", "All Files (*)"
        )
        if file_path:
            self.key_path_edit.setText(file_path)
    
    def get_config(self):
        config = {
            'host': self.host_edit.text(),
            'port': self.port_spin.value(),
            'username': self.username_edit.text(),
            'remote_file': self.remote_file_edit.text()
        }
        
        if self.use_key.isChecked():
            config['key_file'] = self.key_path_edit.text()
        else:
            config['password'] = self.password_edit.text()
        
        return config