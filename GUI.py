import sys
import os
import os.path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QFileDialog, QApplication
from PyQt5.uic import loadUi
from Downloader import downloadDrive, getAmountDownloaded, getFilesDownloaded, getFolderData
from PyQt5.QtCore import QTimer, QTime, Qt
from qt_material import apply_stylesheet, list_themes


class MainWindow(QDialog):
    global path
    path = r'C:\Drive Downloader'

    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('GUI.ui', self)
        self.browse.clicked.connect(self.browseFiles)
        self.download.clicked.connect(self.downloadClicked)
        self.signOutButton.clicked.connect(self.signOut)


    
    def signOut(self):
        if os.path.isfile('token_drive_v3.pickle'):
            os.remove('token_drive_v3.pickle') 


    def updateProgressBar(self):
        count = getFilesDownloaded()
        size = getAmountDownloaded()
        folder_data = getFolderData()
        self.progressBar.setValue(count / folder_data)
        if size > 1000000000:
            self.progresBarLabel.setText(u'Downloaded {0} GBs'.format(round(size / 1000000000)))
        else:
            self.progresBarLabel.setText(u'Downloaded {0} MBs'.format(round(size / 1048576,2)))

    
    def downloadClicked(self):
        downloadDrive(path)
        
        # Call function every second to update progress bar
        timer = QTimer(self)
        timer.timeout.connect(self.updateProgressBar)
        timer.start(1000)

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