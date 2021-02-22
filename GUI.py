import sys
import os
import os.path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QLabel
from PyQt5.uic import loadUi
from Downloader import downloadDrive
from PyQt5.QtCore import QTimer, QTime, Qt
from qt_material import apply_stylesheet, list_themes
from PyQt5.QtGui import QMovie


class MainWindow(QDialog):
    global path
    path = r'C:\Drive Downloader'

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('GUI.ui', self)

        label = QLabel(self)
        label.setText("Window Title")
        self.setWindowTitle("Window Title")

        self.browse.clicked.connect(self.browseFiles)
        self.download.clicked.connect(self.downloadClicked)
        self.signOutButton.clicked.connect(self.signOut)

    def signOut(self):
        if os.path.isfile('token_drive_v3.pickle'):
            os.remove('token_drive_v3.pickle')

    def downloadClicked(self):
        self.loadingGIFlabel.setText(
            'Downloading drive ... this may take a while.')
        downloadDrive(path)
        self.loadingGIFlabel.setText('Finished downloading!')

    def browseFiles(self):
        global path
        fname = QFileDialog.getExistingDirectory(self, 'Driver Downloader',
                                                 r'C:\Drive Downloader')
        self.folderPath.setText(fname)
        path = fname


def window():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()

    # setup stylesheet
    # apply_stylesheet(app, theme='dark_blue.xml')

    widget = QtWidgets.QStackedWidget()
    widget.addWidget(mainWindow)
    widget.setFixedHeight(720)
    widget.setFixedWidth(1280)

    widget.show()
    sys.exit(app.exec_())


window()
