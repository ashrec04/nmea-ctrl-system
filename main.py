import asyncio
from qasync import QEventLoop
import sys
import os
from PyQt6.QtWidgets import QApplication

from gui.gui import MainWindow

def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app) # initises the gui through asyncio
    asyncio.set_event_loop(loop)

    window = MainWindow(loop)
    window.show()


if __name__ == "__main__":
    main()