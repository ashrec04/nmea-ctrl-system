import asyncio
from qasync import QEventLoop
import sys
import os
from PyQt6.QtWidgets import QApplication

from gui.gui import MainWindow

def main():

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()