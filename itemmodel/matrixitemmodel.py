from __future__ import annotations

from PySide6.QtWidgets import QTableView, QApplication
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex


class MatrixItemModel(QAbstractTableModel):
    COLNAMES = []

    def __init__(self, result: list[tuple], parent = None):
        QAbstractTableModel.__init__(self, parent)
        self._result = result
    
    def rowCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self._result)
        return 0
    
    def columnCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self.__class__.COLNAMES)
        return 0
    
    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        if not index.isValid():
            return None
        
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._result[index.row()][index.column()])
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.__class__.COLNAMES[section]
        
        return None

