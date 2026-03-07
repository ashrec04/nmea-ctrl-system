from PyQt6.QtWidgets import QMainWindow
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

from PyQt6 import uic

import pyqtgraph as pg
import time
from datetime import datetime

#~~ Global Constants
WINDOW_PATH = 'gui/resources/mainwindow.ui'

LIGHT_BLUE = "#E3F6FD"
DARK_BLUE = "#0B76A0"
TEAL_GREEN = "#1AA5A2"
MAX_GRAPH_POINTS = 50
SENSOR_META = {
  "128267": {"title": "Water Depth", "axis": "Depth (m)"},
  "129026": {"title": "Speed Over Ground", "axis": "Speed (Knots)"},
  "130306": {"title": "Wind Data", "axis": "Speed (Knots)"}
}

#~~

class MinuteAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        labels = []
        for value in values:
            try:
                labels.append(datetime.fromtimestamp(value).strftime("%H:%M"))
            except (ValueError, OSError, OverflowError):
                labels.append("")
        return labels

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
        
        ## current Graphs and label info
        self.graph_data = {}
        self.graph_widgets = {}

        self.label_data = {}
        self.data_widgets = {}

        self.graph_columns = 2
        self.data_columns = 2

        self.graphGridLayout.setContentsMargins(12, 12, 12, 12)
        self.graphGridLayout.setHorizontalSpacing(12)
        self.graphGridLayout.setVerticalSpacing(12)

        self.dataGridLayout.setContentsMargins(12, 12, 12, 12)
        self.dataGridLayout.setHorizontalSpacing(12)
        self.dataGridLayout.setVerticalSpacing(12)
        self.dataGridLayout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )


    def DataInput(self, pgn, value):
        graph_name = str(pgn)
        if graph_name not in self.graph_data:
            self.AddGraph(graph_name)
            self.AddDataWidget(graph_name)

        self.AddGraphPlot(graph_name, value)
        self.UpdateDataLabel(graph_name, value)


    def AddGraph(self, pgn):
        plot_graph = pg.PlotWidget(axisItems={"bottom": MinuteAxisItem(orientation="bottom")})
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

        graph_meta = SENSOR_META.get(pgn, {"title": f"PGN {pgn}", "axis": "Value"})

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

        self.graph_data[pgn] = {"x": [], "y": [], "line": graph_line}
        self.graph_widgets[pgn] = plot_graph


    def AddGraphPlot(self, pgn, value):
        g = self.graph_data.get(pgn)

        try:
            y_value = float(value)
        except (TypeError, ValueError) as e:
            print("ADDING PLOT ERROR: ", e)
            return

        g["x"].append(time.time())
        g["y"].append(y_value)

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


    def AddDataWidget(self, pgn):
        sensor_meta = SENSOR_META.get(pgn, {"title": f"PGN {pgn}", "axis": "Value"})

        data_widget = QtWidgets.QWidget() # widget holding title & data label
        data_widget_layout = QtWidgets.QVBoxLayout(data_widget)

        data_widget.setStyleSheet( # colour widget bg and make it look rounded
            f"background-color: {DARK_BLUE};"
            f"border: 1px solid {DARK_BLUE};"
            "border-radius: 12px;"
        )

        data_widget.setMaximumSize(QSize(400,200))
        data_widget.setMinimumSize(QSize(200, 200))
        data_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Preferred
        )


        #declare labels & their text
        title_label = QtWidgets.QLabel(sensor_meta["title"])
        data_val_label = QtWidgets.QLabel("0.0")

        #set alignment
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        data_val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #set font size & colour
        title_label.setFont(QFont("Verdana", 18))
        title_label.setStyleSheet(f"color: {LIGHT_BLUE};")
        data_val_label.setFont(QFont("Verdana", 20, QFont.Weight.Bold))
        data_val_label.setStyleSheet(f"color: {LIGHT_BLUE};")


        data_widget_layout.addWidget(title_label)
        data_widget_layout.addWidget(data_val_label)

        widget_index = len(self.data_widgets)
        row = widget_index // self.data_columns
        column = widget_index % self.data_columns


        self.dataGridLayout.addWidget(data_widget, row, column)  # put in grid
        self.dataGridLayout.setRowStretch(row, 1)
        self.dataGridLayout.setColumnStretch(column, 1)

        self.label_data[pgn] = data_val_label
        self.data_widgets[pgn] = data_widget



    def UpdateDataLabel(self, pgn, value):

        label = self.label_data.get(pgn)
        
        if label is not None:
            label.setText(str(round(value, 2))) #show val on screen rounded to 2dp
