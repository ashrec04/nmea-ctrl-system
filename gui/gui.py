import asyncio
from PyQt6.QtWidgets import QMainWindow, QLabel, QScrollArea
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QTimer

from PyQt6 import uic

import pyqtgraph as pg


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

        self.pen = pg.mkPen(color=DARK_BLUE ,width=5)
        self.title_style = {"color": TEAL_GREEN, "font-size": "18px"}
        self.axis_style = {"color": TEAL_GREEN, "font-size": "18px"}
        self.graph_data = {}
        self.max_points = 100

    def DataInput(self, pgn, value):
        graph_name = str(pgn)
        if graph_name not in self.graph_data:
            self.AddGraph(graph_name)

        self.AddGraphPlot(graph_name, value)


    def AddGraph(self, pgn):
        graph_name = str(pgn)

        plot_graph = pg.PlotWidget()
        plot_graph.setObjectName(graph_name)
        self.graphGridLayout.addWidget(plot_graph)  # put in grid

        plot_graph.setBackground("w")
        plot_graph.setTitle(f"{graph_name} vs Time", **self.title_style)
        plot_graph.setLabel("left", "Value", **self.axis_style)  # y axis
        plot_graph.setLabel("bottom", "Sample", **self.axis_style)  # x axis
        plot_graph.showGrid(x=True, y=True)

        line = plot_graph.plot([], [], pen=self.pen)
        self.graph_data[graph_name] = {"x": [], "y": [], "line": line}

    def AddGraphPlot(self, graph_name, value):
        graph_name = str(graph_name)
        graph = self.graph_data.get(graph_name)

        if graph is None:
            self.AddGraph(graph_name)
            graph = self.graph_data[graph_name]

        try:
            y_value = float(value)
        except (TypeError, ValueError):
            return

        next_x = graph["x"][-1] + 1 if graph["x"] else 0
        graph["x"].append(next_x)
        graph["y"].append(y_value)

        if len(graph["x"]) > self.max_points:
            graph["x"] = graph["x"][-self.max_points:]
            graph["y"] = graph["y"][-self.max_points:]

        graph["line"].setData(graph["x"], graph["y"])
    
    
