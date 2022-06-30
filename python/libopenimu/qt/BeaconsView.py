from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QTabWidget
from PySide6.QtCore import Slot, Signal, QPointF

from libopenimu.qt.BaseGraph import BaseGraph
import datetime


class BeaconsView(QTabWidget, BaseGraph):

    # aboutToClose = Signal(QObject)
    cursorMoved = Signal(float)

    def __init__(self, parent):
        BaseGraph.__init__(self, parent=parent)
        QTabWidget.__init__(self, parent=parent)

        self.tabDict = {}

    def setCursorPositionFromTime(self, timestamp, emit_signal=False):
        pass

    def zoom_reset(self):
        pass

    def zoom_in(self):
        pass

    def zoom_out(self):
        pass

    def clearSelectionArea(self, emit_signal=False):
        pass

    def setSelectionAreaFromTime(self, start_time, end_time, emit_signal=False):
        self.clearSelectionArea()
        pass

    def add_tab(self, label, count):
        table_widget = QTableWidget(self)
        table_widget.setColumnCount(2)
        table_widget.setRowCount(count)
        table_widget.setAutoScroll(True)
        table_widget.setColumnWidth(0, 300)
        table_widget.setColumnWidth(1, 200)
        table_widget.setHorizontalHeaderItem(0, QTableWidgetItem('Time'))
        table_widget.setHorizontalHeaderItem(1, QTableWidgetItem('Value'))
        split_label = label.split('_')
        if len(split_label) == 3:
            self.addTab(table_widget, split_label[2] + ' [' + str(split_label[1]) + ']')
        else:
            self.addTab(table_widget, label)

        self.tabDict[label] = table_widget

    def add_row(self, row, time, value, label):
        if self.tabDict.__contains__(label):
            if row < self.tabDict[label].rowCount():
                # Time
                self.tabDict[label].setItem(row, 0, QTableWidgetItem(str(datetime.datetime.fromtimestamp(time))))

                # Value
                self.tabDict[label].setItem(row, 1, QTableWidgetItem(str(value)))
            else:
                print('out of range : ', row)

    @property
    def is_zoomed(self):
        return False
