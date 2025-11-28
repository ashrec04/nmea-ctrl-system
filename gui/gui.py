from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QScrollArea

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        
        # removes windows title bar and borders
        #self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        # force always on top
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        # force fullscreen
        self.showFullScreen()

        label = QLabel("ur trapped rn fella", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(label)

    # Ignore all attempts to close the window
    def closeEvent(self, event):
        event.ignore()