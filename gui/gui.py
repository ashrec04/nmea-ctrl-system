from PyQt6.QtWidgets import QMainWindow
from PyQt6 import QtWidgets

from PyQt6 import uic

import pyqtgraph as pg

#~~ Global Constants
WINDOW_PATH = 'gui/resources/mainwindow.ui'

LIGHT_BLUE = "#E3F6FD"
DARK_BLUE = "#0B76A0"
TEAL_GREEN = "#1AA5A2"
MAX_GRAPH_POINTS = 50

GRAPH_META = {
  "128267": {"title": "Water Depth", "axis": "Depth (m)"},
  "129026": {"title": "Speed Over Ground", "axis": "Speed (Knots)"},
  "130306": {"title": "Wind Data", "axis": "Speed (Knots)"}
}

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

        self.pen = pg.mkPen(color=DARK_BLUE ,width=3)
        self.title_style = {"color": TEAL_GREEN, "font-size": "18px"}
        self.axis_style = {"color": TEAL_GREEN, "font-size": "18px"}
        self.graph_data = {}
        self.graph_widgets = {}
        self.graph_columns = 2

        self.graphGridLayout.setContentsMargins(12, 12, 12, 12)
        self.graphGridLayout.setHorizontalSpacing(12)
        self.graphGridLayout.setVerticalSpacing(12)


    def DataInput(self, pgn, value):
        graph_name = str(pgn)
        if graph_name not in self.graph_data:
            self.AddGraph(graph_name)

        self.AddGraphPlot(graph_name, value)


    def AddGraph(self, pgn):
        plot_graph = pg.PlotWidget()
        plot_graph.setObjectName(pgn)
        plot_graph.setMinimumHeight(260)
        plot_graph.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        graph_index = len(self.graph_widgets)
        row = graph_index // self.graph_columns
        column = graph_index % self.graph_columns

        self.graphGridLayout.addWidget(plot_graph, row, column)  # put in grid
        self.graphGridLayout.setRowStretch(row, 1)
        self.graphGridLayout.setColumnStretch(column, 1)

        plot_graph.show()

        graph_meta = GRAPH_META.get(pgn, {"title": f"PGN {pgn}", "axis": "Value"})

        plot_graph.setBackground(LIGHT_BLUE)
        plot_graph.setTitle(graph_meta["title"], **self.title_style)
        plot_graph.setLabel("left", graph_meta["axis"], **self.axis_style) # y axis
        plot_graph.setLabel("bottom", "Time", **self.axis_style) # x axis
        plot_graph.getAxis("bottom").enableAutoSIPrefix(False)

        plot_graph.showGrid(x=True, y=True)

        graph_line = plot_graph.plot(
            [], # x plot
            [], # y plot
            pen=self.pen # line style
        )

        self.graph_data[pgn] = {"x": [], "y": [], "line": graph_line, "next_x": 0}
        self.graph_widgets[pgn] = plot_graph


    def AddGraphPlot(self, pgn, value):
        g = self.graph_data.get(pgn)

        try:
            y_value = float(value)
        except (TypeError, ValueError) as e:
            print("ADDING PLOT ERROR: ", e)
            return

        g["x"].append(g["next_x"])
        g["y"].append(y_value)
        g["next_x"] += 1

        if len(g["x"]) > MAX_GRAPH_POINTS:  # keeps only 50 points on graph at once
            g["x"] = g["x"][-MAX_GRAPH_POINTS:]
            g["y"] = g["y"][-MAX_GRAPH_POINTS:]

        g["line"].setData(g["x"], g["y"])
        plot_graph = self.graph_widgets.get(pgn)

        if plot_graph is not None:
            plot_graph.enableAutoRange(axis="x", enable=True)
            plot_graph.enableAutoRange(axis="y", enable=True)
            plot_graph.update()
            plot_graph.repaint()

        self.graph_data[pgn] = g
