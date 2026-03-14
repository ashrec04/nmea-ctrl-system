from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

import pyqtgraph as pg
import time
from datetime import datetime


#~~ Global Constants
LIGHT_BLUE = "#E3F6FD"
DARK_BLUE = "#0B76A0"
TEAL_GREEN = "#1AA5A2"
MAX_GRAPH_POINTS = 50
SENSOR_META = {
  "128267": {"title": "Water Depth", "axis": "Depth (m)", "unit": "Meters"},
  "129026": {"title": "Speed Over Ground", "axis": "Speed (Knots)", "unit": "Knots"},
  "130306": {"title": "Wind Data", "axis": "Speed (Knots)", "unit": "Knots"},
  "127505": {"title": "Bilge Level", "axis": "", "unit": "L"},
  "127488": {"title": "Engine Status", "axis": "", "unit": "rpm"},
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


class GraphWidget:
    def __init__(self, pgn, sensor_meta):

        self.pgn = pgn
        self.graph_meta = sensor_meta

        self.pen = pg.mkPen(color=DARK_BLUE, width=3)
        self.title_style = {"color": TEAL_GREEN, "font-size": "18px"}
        self.axis_style = {"color": TEAL_GREEN, "font-size": "18px"}
        
        self.x = []
        self.y = []

        self.g = pg.PlotWidget(
            axisItems={"bottom": MinuteAxisItem(orientation="bottom")} # x axis set to hh:mm (24 hrs)
        )
        self.g.setObjectName(pgn)
        self.g.setMinimumHeight(260)
        self.g.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.g.setBackground(LIGHT_BLUE)
        self.g.setTitle(self.graph_meta["title"], **self.title_style) # graph title
        self.g.setLabel("left", self.graph_meta["axis"], **self.axis_style) # y axis name
        self.g.setLabel("bottom", "Time", **self.axis_style) #x axis name
        self.g.getAxis("bottom").enableAutoSIPrefix(False)
        self.g.showGrid(x=True, y=True)

        self.line = self.g.plot(
            [], # x plot
            [], # y plot
            pen=self.pen # line style
        )


    def AddPoint(self, value):
        try:
            y_value = float(value)
        except (TypeError, ValueError):
            return

        self.x.append(time.time())
        self.y.append(y_value)

        if len(self.x) > MAX_GRAPH_POINTS: # keeps only 50 points on graph at once
            self.x = self.x[-MAX_GRAPH_POINTS:]
            self.y = self.y[-MAX_GRAPH_POINTS:]

        self.line.setData(self.x, self.y)
        self.g.enableAutoRange(axis="x", enable=True)
        self.g.enableAutoRange(axis="y", enable=True)


class DataWidget:
    def __init__(self, pgn, sensor_meta):

        self.pgn = pgn
        self.sensor_meta = sensor_meta
        self.update_count = 0
        self.update_interval = 5

        self.d = QtWidgets.QWidget() # widget holding title & data label
        d_layout = QtWidgets.QVBoxLayout(self.d)

        self.d.setStyleSheet( # colour widget bg and make it look rounded
            f"background-color: {DARK_BLUE};"
            f"border: 1px solid {DARK_BLUE};"
            "border-radius: 12px;"
        )

        self.d.setMaximumSize(QSize(400, 200))
        self.d.setMinimumSize(QSize(200, 200))
        self.d.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Preferred
        )

        #declare labels & their text
        title_label = QtWidgets.QLabel(self.sensor_meta["title"])
        self.value_label = QtWidgets.QLabel("0.0")

        #set alignment
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #set font size & colour
        title_label.setFont(QFont("Verdana", 18))
        title_label.setStyleSheet(f"color: {LIGHT_BLUE};")
        self.value_label.setFont(QFont("Verdana", 20, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {LIGHT_BLUE};")

        d_layout.addWidget(title_label)
        d_layout.addWidget(self.value_label)


    def UpdateData(self, value):
        
        if self.update_count >= self.update_interval: # only update data at every 5th recieved
            self.update_count = 0
            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                return
            self.value_label.setText(
                f"{round(numeric_value, 2)} {self.sensor_meta['unit']}"
            ) #show val on screen rounded to 1dp
        
        else:
            self.update_count += 1

class AlarmWidget:
    def __init__(self, pgn, sensor_meta):

        self.pgn = pgn
        self.sensor_meta = sensor_meta
        self.update_count = 0
        self.update_interval = 5

        self.d = QtWidgets.QWidget() # widget holding title & data label
        d_layout = QtWidgets.QVBoxLayout(self.d)

        self.d.setStyleSheet( # colour widget bg and make it look rounded
            f"background-color: {DARK_BLUE};"
            f"border: 1px solid {DARK_BLUE};"
            "border-radius: 12px;"
        )

        self.d.setMaximumSize(QSize(400, 200))
        self.d.setMinimumSize(QSize(200, 200))
        self.d.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Preferred
        )

        #declare labels & their text
        title_label = QtWidgets.QLabel(f"{self.sensor_meta["title"]} Alarm ")
        self.type_label = QtWidgets.QLabel("Trigger when:")
        self.value_label = QtWidgets.QLabel("Than:")


        #set alignment
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #set font size & colour
        title_label.setFont(QFont("Verdana", 18))
        title_label.setStyleSheet(f"color: {LIGHT_BLUE};")
        self.value_label.setFont(QFont("Verdana", 20, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {LIGHT_BLUE};")
        self.type_label.setFont(QFont("Verdana", 20, QFont.Weight.Bold))
        self.type_label.setStyleSheet(f"color: {LIGHT_BLUE};")

        d_layout.addWidget(title_label)
        d_layout.addWidget(self.value_label)
        d_layout.addWidget(self.type_label)
    
