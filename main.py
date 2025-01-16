from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from view.mainwindow_ui import Ui_MainWindow
from model import MainModel
from itemmodel import *


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.pluginsView.expandAll()
        self.splitter.setSizes([1, 3])

        self.model = MainModel()

        self.openAction.triggered.connect(self.openMemDump)
        self.pluginsView.itemDoubleClicked.connect(self.analyse)

    @Slot()
    def openMemDump(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', './')
        if fname:
            self.model.open_image(fname)
            self.log(f"다음과 같은 메모리를 탑재하였습니다. ==> {fname}")
    
    @Slot(QTreeWidgetItem)
    def analyse(self, item: QTreeWidgetItem):
        match item.text(0):
            case "windows.pslist.PsList":
                self.log("windows.pslist.PsList 를 시작하였습니다.")
                model = PsListModel(self.model.run_ps_list(lambda p, d: self.log(f"{p}: {d}")))
                self.resultView.setModel(model)
                self.log("windows.pslist.PsList 가 종료되었습니다.")

            case "windows.psscan.PsScan":
                self.log("windows.psscan.PsScan 을 시작하였습니다.")
                model = PsScanModel(self.model.run_ps_scan(lambda p, d: self.log(f"{p}: {d}")))
                self.resultView.setModel(model)
                self.log("windows.psscan.PsScan 이 종료되었습니다.")

            case "windows.filescan.FileScan":
                self.log("windows.filescan.FileScan 을 시작하였습니다.")
                model = FileScanModel(self.model.run_file_scan(lambda p, d: self.log(f"{p}: {d}")))
                self.resultView.setModel(model)
                self.log("windows.filescan.FileScan 이 종료되었습니다.")

    def log(self, msg):
        self.logsView.appendPlainText(msg)
        self.repaint()

if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()
