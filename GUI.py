from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QFileDialog, QApplication
from PyQt5.uic import loadUi
from Downloader import downloadDrive
import sys


class MainWindow(QDialog):
    global path
    path = r'C:\Drive Downloader'

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('GUI.ui', self)
        self.browse.clicked.connect(self.browseFiles)
        self.download.clicked.connect(self.downloadClicked)
    
    def downloadClicked(self):
        downloadDrive(path)

    def browseFiles(self):
        global path
        fname = QFileDialog.getExistingDirectory(self, 'Driver Downloader',
                                                 r'C:\Drive Downloader')
        self.folderPath.setText(fname)
        path = fname


def window():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(mainWindow)
    widget.setFixedHeight(720)
    widget.setFixedWidth(1200)
    widget.show()
    sys.exit(app.exec_())

window()