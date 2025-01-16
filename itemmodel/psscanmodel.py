from __future__ import annotations

from PySide6.QtWidgets import QTableView, QApplication
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex

from .matrixitemmodel import MatrixItemModel


class PsScanModel(MatrixItemModel):
    """A model to interface a Qt view with PsScan result"""
    COLNAMES = [
            "PID", "PPID",
            "Filename", "Offset",
            "Threads", "Handles",
            "Session ID",
            "is WOW64",
            "Create Time",
            "Exit Time",
            "File Output"]
