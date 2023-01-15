from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialogButtonBox, QDialog, QVBoxLayout, QLabel, QStyle


class ExitDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Exit Dialog")
        windowIcon = self.style().standardIcon(QStyle.SP_BrowserStop)
        self.setWindowIcon(windowIcon)

        QBtn = QDialogButtonBox.Yes | QDialogButtonBox.No
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.setCenterButtons(True)

        self.layout = QVBoxLayout()
        font = QFont('Calibri', 10, weight=QFont.Bold)
        message = QLabel("You are going to exit the Music Player application!")
        messagev2 = QLabel("Are you sure?")
        messagev2.setFont(font)
        self.layout.addWidget(message)
        self.layout.addWidget(messagev2)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.show()
