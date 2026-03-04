import asyncio
from PyQt6.QtWidgets import QMainWindow, QLabel, QScrollArea
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QTimer

from PyQt6 import uic

import pyqtgraph as pg

from random import randint


#~~ Global Constants
WINDOW_PATH = 'gui/resources/mainwindow.ui'

LIGHT_BLUE = "#E3F6FD"
DARK_BLUE = "#0B76A0"
TEAL_GREEN = "#1AA5A2"
#~~

# Subclass QMainWindow to customise the window
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        uic.loadUi(WINDOW_PATH, self)   # loads window as defined in mainwindow.ui

        # Temperature vs time dynamic plot
        self.plot_graph = pg.PlotWidget()
        self.graphGridLayout.addWidget(self.plot_graph)  # put in grid

        self.plot_graph.setBackground("w")
        pen = pg.mkPen(color=DARK_BLUE, width=5)
        self.plot_graph.setTitle("Temperature vs Time", color="b", size="20pt")
        styles = {"color": "red", "font-size": "18px"}
        self.plot_graph.setLabel("left", "Temperature (°C)", **styles)
        self.plot_graph.setLabel("bottom", "Time (min)", **styles)
        self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)
        self.plot_graph.setYRange(20, 40)
        self.time = list(range(10))
        self.temperature = [randint(20, 40) for _ in range(10)]
        # Get a line reference
        self.line = self.plot_graph.plot(
            self.time,
            self.temperature,
            name="Temperature Sensor",
            pen=pen,
            symbol="+",
            symbolSize=15,
            symbolBrush="b",
        )
        # Add a timer to simulate new temperature measurements
        self.timer = QTimer()
        self.timer.setInterval(300)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def AddGraph(self):
        styles = {"color": TEAL_GREEN, "font-size": "18px"}

        self.plot_graph = pg.PlotWidget()
        self.graphGridLayout.addWidget(self.plot_graph)  # put in grid

        self.plot_graph.setBackground("w")
        pen = pg.mkPen(color=DARK_BLUE ,width=5)
        self.plot_graph.setTitle("Temperature vs Time", color=TEAL_GREEN, size="20pt")
        self.plot_graph.setLabel("left", "Temperature (°C)", **styles) # y axis
        self.plot_graph.setLabel("bottom", "Time (min)", **styles) # x axis
        self.plot_graph.showGrid(x=True, y=True)
        self.plot_graph.setXRange(1, 10)
        self.plot_graph.setYRange(20, 40)

        minutes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [32, 33, 31, 29, 32, 35, 30, 30, 32, 34]

        self.plot_graph.plot(minutes, temperature, pen=pen)

    def update_plot(self):
        self.time = self.time[1:]
        self.time.append(self.time[-1] + 1)
        self.temperature = self.temperature[1:]
        self.temperature.append(randint(20, 40))
        self.line.setData(self.time, self.temperature)
    
    