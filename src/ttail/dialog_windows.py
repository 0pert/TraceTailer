from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("About")

        QBtn = (
            QDialogButtonBox.StandardButton.Ok  # | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        # self.buttonBox.   rejected.connect(self.reject)

        layout = QVBoxLayout()
        label = QLabel()
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setText("""
    <span style='font-size: 16pt;'><b>TraceTailer - </b></span><span style='font-size: 11pt;'>v0.1.2<br>
    © 2026 Oliver Broman<br><br>
    Kontakt: <a href='mailto:oliver@bytesofit.se'>oliver@bytesofit.se</a><br>
    GitHub: <a href='https://github.com/0pert/TraceTailer.git'>github.com/Opert/TraceTailer</a></span><br><br>
    <span style='font-size: 11pt;'>Built with Python 3.14 and PyQt6</span>
""")

        label.setOpenExternalLinks(True)

        layout.addWidget(label)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
