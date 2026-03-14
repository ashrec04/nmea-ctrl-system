from PyQt6.QtWidgets import QButtonGroup, QMainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from PyQt6 import uic

import pyqtgraph as pg
from gui.widget_presets import GraphWidget, DataWidget, AlarmWidget

#~~ Global Constants
WINDOW_PATH = 'gui/resources/mainwindow.ui'
ICON_PATH = 'gui/resources/icon.png'

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

        #insert logo into boatSenseIconLabel
        self.boatSenseIconLabel.setPixmap(
            QPixmap(ICON_PATH).scaled(
                50, 50,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

        self.graph_widgets: dict[str, GraphWidget] = {} # dictionary with pgn : GraphWidget
        self.graph_columns = 2

        self.data_widgets: dict[str, DataWidget] = {} # dictionary with pgn : DataWidget
        self.data_columns = 2

        self.alarm_widgets: dict[str, GraphWidget] = {} # dictionary with pgn : AlarmWidget
        self.alarm_columns = 1


        self.daytime_changed_callback = None

        self.graphGridLayout.setContentsMargins(12, 12, 12, 12)
        self.graphGridLayout.setHorizontalSpacing(12)
        self.graphGridLayout.setVerticalSpacing(12)

        self.dataGridLayout.setContentsMargins(12, 12, 12, 12)
        self.dataGridLayout.setHorizontalSpacing(12)
        self.dataGridLayout.setVerticalSpacing(12)
        self.dataGridLayout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        self.alarmGridLayout.setContentsMargins(12, 12, 12, 12)
        self.alarmGridLayout.setHorizontalSpacing(12)
        self.alarmGridLayout.setVerticalSpacing(12)
        self.alarmGridLayout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        #~ day night radio button grouping
        self.daytime = True

        self.day_night_group = QButtonGroup(self)
        self.day_night_group.setExclusive(True)
        self.day_night_group.addButton(self.dayRadioButton)
        self.day_night_group.addButton(self.nightRadioButton)

        self.dayRadioButton.toggled.connect(self.UpdateDaytime)
        self.dayRadioButton.setChecked(self.daytime)
        self.nightRadioButton.setChecked(not self.daytime)


    def DataInput(self, pgn, value):
        input_name = str(pgn)
        sensor_meta = SENSOR_META.get(input_name, {"title": f"PGN {pgn}", "axis": "", "unit": ""})
        has_graph = bool(sensor_meta.get("axis"))

        if input_name not in self.data_widgets:
            #~ Make new Graph Widget if pgn has axis
            if input_name not in self.graph_widgets and has_graph:
                graph_widget = GraphWidget(input_name, sensor_meta)
                self.graph_widgets[input_name] = graph_widget # save to dict

                graph_index = len(self.graph_widgets) - 1
                row = graph_index // self.graph_columns
                column = graph_index % self.graph_columns

                self.graphGridLayout.addWidget(graph_widget.g, row, column)
                self.graphGridLayout.setRowStretch(row, 1)
                self.graphGridLayout.setColumnStretch(column, 1)
                graph_widget.g.show()
            #~ 

            #~ Make new Data Widget
            data_widget = DataWidget(input_name, sensor_meta)
            self.data_widgets[input_name] = data_widget # save to dict

            data_index = len(self.data_widgets) - 1
            row = data_index // self.data_columns
            column = data_index % self.data_columns

            self.dataGridLayout.addWidget(data_widget.d, row, column)
            self.dataGridLayout.setRowStretch(row, 1)
            self.dataGridLayout.setColumnStretch(column, 1)
            data_widget.d.show()
            #~ 

            #~ Make new Alarm Widget only for non-graph PGNs
            if sensor_meta.get("title") == "Bilge Level":
                alarm_widget = AlarmWidget(input_name, sensor_meta)
                self.alarm_widgets[input_name] = alarm_widget # save to dict

                alarm_index = len(self.alarm_widgets) - 1
                row = alarm_index // self.alarm_columns
                column = alarm_index % self.alarm_columns

                self.alarmGridLayout.addWidget(alarm_widget.d, row, column)
                alarm_widget.d.show()
                #~ 


        #~ add/update widgets in all views
        graph_widget = self.graph_widgets.get(input_name)
        if graph_widget is not None:
            graph_widget.AddPoint(value)

        data_widget = self.data_widgets[input_name]
        data_widget.UpdateData(value)

    def UpdateDaytime(self, checked):
        if checked:
            self.daytime = True
        elif self.nightRadioButton.isChecked():
            self.daytime = False

        if self.daytime_changed_callback is not None:
            self.daytime_changed_callback(self.daytime)
