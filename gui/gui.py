import asyncio
import json
import ctypes

from qasync import QEventLoop, asyncSlot

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QScrollArea

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("NMEA Ctrl sys")
        button = QPushButton("testing")

        # Set central widget of Window
        self.setCentralWidget(button)