from PyQt6.QtWidgets import QMainWindow
from PyQt6 import QtWidgets

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

        pg.setConfigOptions(
            background="w",
            foreground=DARK_BLUE,
            antialias=True,
            useOpenGL=False,
        )

        uic.loadUi(WINDOW_PATH, self)   # loads window as defined in mainwindow.ui

        self.pen = pg.mkPen(color=DARK_BLUE ,width=5)
        self.title_style = {"color": TEAL_GREEN, "font-size": "18px"}
        self.axis_style = {"color": TEAL_GREEN, "font-size": "18px"}
        self.graph_data = {}
        self.graph_widgets = {}
        self.graph_columns = 1

        self.graph_time = 0
        self.graphGridLayout.setContentsMargins(12, 12, 12, 12)
        self.graphGridLayout.setHorizontalSpacing(12)
        self.graphGridLayout.setVerticalSpacing(12)


    def DataInput(self, pgn, value):
        graph_name = str(pgn)
        if graph_name not in self.graph_data:
            self.AddGraph(graph_name)

        self.AddGraphPlot(graph_name, value)


    def AddGraph(self, pgn):
        graph_name = str(pgn)

        plot_graph = pg.PlotWidget()
        plot_graph.setObjectName(graph_name)
        plot_graph.setMinimumHeight(260)
        plot_graph.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        # plot_graph.setStyleSheet(f"border: 2px solid {DARK_BLUE};")

        graph_index = len(self.graph_widgets)
        row = graph_index // self.graph_columns
        column = graph_index % self.graph_columns
        self.graphGridLayout.addWidget(plot_graph, row, column)  # put in grid

        self.graphGridLayout.setRowStretch(row, 1)
        self.graphGridLayout.setColumnStretch(column, 1)

        plot_graph.show()

        plot_graph.setBackground("w")
        plot_graph.setTitle(graph_name, **self.title_style)
        plot_graph.setLabel("left", "Depth (m)", **self.axis_style) # y axis
        plot_graph.setLabel("bottom", "Time", **self.axis_style) # x axis

        plot_graph.showGrid(x=True, y=True)
        plot_graph.setYRange(0, 40)

        graph_line = plot_graph.plot(
            [], # x plot
            [], # y plot
            pen=self.pen # line style
        )
        
        self.graph_data[graph_name] = {"x": [], "y": [], "line": graph_line}
        self.graph_widgets[graph_name] = plot_graph


    def AddGraphPlot(self, graph_name, value):

        graph_name = str(graph_name)
        g = self.graph_data.get(graph_name)

        try:
            y_value = float(value)
        except (TypeError, ValueError):
            return

        g["x"].append(self.graph_time)
        g["y"].append(y_value)

        self.graph_time += 1

        g["line"].setData(g["x"], g["y"])
        plot_graph = self.graph_widgets.get(graph_name)

        if plot_graph is not None:
            plot_graph.enableAutoRange(axis="x", enable=True)
            plot_graph.enableAutoRange(axis="y", enable=True)
            plot_graph.update()
            plot_graph.repaint()

        self.graph_data[graph_name] = g        
    
    
