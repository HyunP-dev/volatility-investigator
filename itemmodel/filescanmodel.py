from __future__ import annotations

from PySide6.QtWidgets import QTableView, QApplication
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex

from .matrixitemmodel import MatrixItemModel


class FileScanModel(MatrixItemModel):
    """A model to interface a Qt view with FileScan result"""
    COLNAMES = ["Offset", "Filename", "Size"]
