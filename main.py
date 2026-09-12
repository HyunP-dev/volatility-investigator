import volatility3
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from model import MainModel
from model.voltreegridmodel import VolTreeGridModel

volatility3.framework.require_interface_version(2, 0, 0)
failures = volatility3.framework.import_files(volatility3.plugins, True)

from volatility3.framework import automagic, contexts, interfaces, plugins
from volatility3.framework.constants import ProgressCallback
from volatility3.framework.renderers import NotApplicableValue, UnreadableValue





class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.addToolBar(toolbar := QToolBar())
        toolbar.addAction(openAction := QAction())
        openAction.setText("Open memory")
        self.openAction = openAction

        splitter = QSplitter()
        self.setCentralWidget(splitter)

        self.pluginsView = QTreeView()
        self.pluginsView.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        self.pluginsView.setRootIsDecorated(False)
        self.pluginsView.setHeaderHidden(True)

        self.pluginsView.setModel(pluginsModel := QStandardItemModel())
        for plugin_name in volatility3.framework.list_plugins():
            pluginsModel.appendRow(QStandardItem(plugin_name))

        self.resultView = QTreeView()
        self.resultView.setRootIsDecorated(False)

        self.logsView = QPlainTextEdit()

        splitter.addWidget(leftTabs := QTabWidget())
        leftTabs.addTab(self.pluginsView, "플러그인")

        splitter.addWidget(rightTabs := QTabWidget())
        rightTabs.addTab(self.resultView, "분석 결과")
        rightTabs.addTab(self.logsView, "로그")

        splitter.setSizes([210, 900])

        self.model = MainModel()
        self.image_path = None

        self.openAction.triggered.connect(self.openMemDump)
        self.pluginsView.doubleClicked.connect(self.analyse)

    @Slot()
    def openMemDump(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open file", "./")
        if fname:
            self.image_path = fname
            self.log(f"다음과 같은 메모리를 탑재하였습니다. ==> {fname}")

    @Slot(QTreeWidgetItem)
    def analyse(self, index: QModelIndex):
        self.log(index.data(Qt.ItemDataRole.DisplayRole) + " 를 시작하였습니다.")
        worker = PluginWorker(self, index.data(Qt.ItemDataRole.DisplayRole), self.image_path)

        def on_progress(p, d):
            self.log(f"{p} : {d}")

        worker.progress.connect(on_progress)

        def on_finish(plugin):
            print("분석은 종료되었음.")
            self.resultView.setModel(VolTreeGridModel(plugin))
            self.log(index.data(Qt.ItemDataRole.DisplayRole) + " 가 종료되었습니다.")

        worker.finish.connect(on_finish)

        worker.start()

    def log(self, msg):
        print(msg)
        self.logsView.appendPlainText(msg)
        self.repaint()


class PluginWorker(QThread):
    finish = Signal(object)
    progress = Signal(float, str)

    @staticmethod
    def construct_runner(
        plugin_name: str, image_path: str, progress_callback: ProgressCallback
    ):
        ctx = contexts.Context()
        automagics = automagic.available(ctx)
        plugin_list = volatility3.framework.list_plugins()
        plugin = plugin_list[plugin_name]
        base_config_path = "plugins"
        ctx.config["automagic.LayerStacker.single_location"] = (
            volatility3.cli.CommandLine.location_from_file(image_path)
        )
        constructed = plugins.construct_plugin(
            ctx,
            automagics,
            plugin,
            base_config_path,
            progress_callback,
            None,
        )
        return constructed

    def __init__(self, parent, plugin: str, image_path: str):
        super().__init__(parent=parent)
        self.plugin = plugin
        self.image_path = image_path

    def run(self):
        plugin = self.construct_runner(
            self.plugin,
            self.image_path,
            lambda p, d: self.progress.emit(p, d),
        )
        self.finish.emit(plugin)


if __name__ == "__main__":
    app = QApplication()
    app.setStyle("fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(0xF7, 0xF7, 0xF7))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0x48, 0x77, 0xD7))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)

    app.setPalette(palette)

    app.setStyleSheet("""
QTreeView {
    border: 0;
}

QHeaderView::section {
    background-color: #fff;
    color: #000;
    padding-left: 4px;
    border: none;
    border-right: 1px solid #e5e5e5;
}

QHeaderView::section:hover {
    background-color: #d9ebf9;
}

QHeaderView::section:checked {
    background-color: #bcdcf4;
}
    """)
    window = MainWindow()
    window.showMaximized()
    app.exec()
