import asyncio
from qasync import asyncSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QLabel, QScrollArea
from PyQt6 import uic


#~~ Global Constants
WINDOW_PATH = 'gui/resources/mainwindow.ui'
#~~

# Subclass QMainWindow to customise the window
class MainWindow(QMainWindow):

    def __init__(self, condition_list, loop=None):
        super().__init__()

        uic.loadUi(WINDOW_PATH, self)   # loads window as defined in mainwindow.ui

