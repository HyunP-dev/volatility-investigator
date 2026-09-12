from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from volatility3.cli.text_renderer import CLIRenderer
from volatility3.framework.interfaces.plugins import PluginInterface
from volatility3.framework.interfaces.renderers import TreeGrid, TreeNode


class VolTreeGridModel(QAbstractTableModel):
    def __init__(self, plugin: PluginInterface, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._plugin = plugin
        self._grid: TreeGrid = plugin.run()

        self._rows = []
        def visitor(node: TreeNode, acc: list):
            row = []
            for column_index, column in enumerate(self._grid.columns):

                renderer = CLIRenderer._type_renderers.get(
                    column.type, CLIRenderer._type_renderers["default"]
                )

                row.append(renderer(node.values[column_index]))
            acc.append(row)
            return acc
            
        self._grid.visit(node=None, function=visitor, initial_accumulator=self._rows)

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self._rows)
        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self._grid.columns)
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            try:
                return self._rows[index.row()][index.column()]
            except IndexError:
                pass
        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ):
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return self._grid.columns[section].name

        return None
