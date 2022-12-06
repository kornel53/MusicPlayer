import sys

from PyQt5.QtWidgets import QApplication, QWidget, QLabel


class MainWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.init_ui()

	def init_ui(self):
		test_label = QLabel("Music Player", self)

		self.setFixedSize(400, 200)
		self.setWindowTitle("Music Player")
		self.show()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec())
