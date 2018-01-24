#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Developer : Al Sabawi
Name : stocks.py
Date : 01/23/2018

"""

import time
from datetime import datetime
import matplotlib.pyplot as plt
from pandas_datareader import DataReader
from pandas_datareader._utils import RemoteDataError
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5 import QtTest
from PyQt5 import QtGui

symb = [
    'AAPL',
    'IBM',
    'MSFT',
    'HPQ',
    'ORCL',
    'FB'
]

startDate = datetime(2017, 7, 1)
endDate = datetime(2018, 1, 22)

data_list = {}
retry_time = 10
retry_count = 3
attempt = 0

class mainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # textEdit = QTextEdit()
        # self.setCentralWidget(textEdit)

        exitAct = QAction(QIcon('exit24.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAct)

        self.cw = ChildWidget()
        self.setCentralWidget(self.cw)

        self.setGeometry(300, 500, 500, 500)
        self.setWindowTitle('Main window')
        self.show()

    def contextMenuEvent(self, event):

        cmenu = QMenu(self)

        newAct = cmenu.addAction("New")
        opnAct = cmenu.addAction("Open")
        quitAct = cmenu.addAction("Quit")
        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        if action == quitAct:
            qApp.quit()

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class ChildWidget(QWidget):
    def __init__(self):
        super(ChildWidget, self).__init__()

        chartbtn = QPushButton('Start Charting', self)
        chartbtn.setToolTip('Start charting stocks')
        chartbtn.clicked.connect(self.genCharts2)
        chartbtn.resize(chartbtn.sizeHint())
        chartbtn.move(1, 1)

    def genCharts2(self,event):
        global symb, attempt,retry_time,retry_count
        i = 0
        for s in symb:
            i += 1
            attempt = 1
            self.parent().statusBar().showMessage('Collecting data for ' + s)
            while not self.getData(self,s) and attempt < retry_count:
                attempt = +1
                #time.sleep(retry_time)
                QtTest.QTest.qWait(retry_time * 1000)
            if attempt < retry_count:
                self.parent().statusBar().showMessage('Charting ' + s)
                self.plotData(self,s)
                self.parent().statusBar().showMessage('Completed ' + s)
                if i < len(symb):
                    #time.sleep(10)
                    QtTest.QTest.qWait(10000)
                else:
                    break
        self.parent().statusBar().showMessage('Done Charting!')

    def getData(self,event,s):
        global data_list
        try:
            data_list[s] = DataReader(s, 'yahoo', startDate, endDate)
            return True
        except RemoteDataError:
            print('Exception : Remote call failed. Will wait for {0} seconds to retry'.format(retry_time))
            return False

    def plotData(self,event,s):
        plt.figure()
        ss = data_list[s]['Adj Close']

        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(s)
        ss.plot().grid(linestyle=':', b=True, which='both', )
        plt.savefig(s+'.png')
        #print("Plotted " + s)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = mainWindow()
    sys.exit(app.exec_())