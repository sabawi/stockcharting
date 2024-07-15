#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Developer : Al Sabawi
Name : stocks.py
Date : 01/23/2018

"""

import sys
from datetime import datetime

import matplotlib.dates as dd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests.exceptions as requests_exceptions
import yfinance as yf
from PyQt5 import QtTest, QtCore
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import *
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
# from matplotlib.finance import candlestick_ohlc
import mplfinance as candlestick_ohlc
from pandas_datareader import DataReader
from pandas_datareader._utils import RemoteDataError
from dialogs import Ui_Settings as Setting_dialog

# Globals
symb = []
endDate = datetime.today()
startDate = endDate.replace( year = endDate.year - 1) ## Go back 1 year

chart_stick_scale = 'day'  # Valid values: day, week, month, year, or n="number of days" in each stick
data_source = 'yahoo' # yahoo, quandl key yYCEL8BqzxYUsgG67FTb


data_list = {}
subwindows = []

wait_between_requests = 0  # Seconds
retry_time = 1  # Seconds
retry_count = 3
attempt = 0

# Globals
imagesLabels = {}
imagesPix = []
imageWinCount = 0


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("SockChartingMainWindow")
        MainWindow.setWindowTitle("Control Center")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


class ControlWindow(QMainWindow):
    resized = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ControlWindow, self).__init__(parent=parent)
        ui = Ui_MainWindow()
        ui.setupUi(self)
        self.statusBar()

        self.mainMenu = self.menuBar()

        self.fileMenu = self.mainMenu.addMenu('&File')
        #       Add file submenu
        self.exitSubMenu = QAction('E&xit', self)
        self.exitSubMenu.setShortcut('Ctrl+x')
        self.exitSubMenu.triggered.connect(self.close)
        self.fileMenu.addAction(self.exitSubMenu)

        #        self.editMenu = self.mainMenu.addMenu('&Edit')

        #        self.viewMenu = self.mainMenu.addMenu('&View')

        self.windowsMenu = self.mainMenu.addMenu('&Windows')
        # add Windows submenu
        self.cascadeSubMenu = QAction('C&ascade', self)
        self.cascadeSubMenu.setShortcut('Ctrl+a')
        self.cascadeSubMenu.triggered.connect(self.cascadeWindows)
        self.windowsMenu.addAction(self.cascadeSubMenu)

        self.tileSubMenu = QAction('&Tile', self)
        self.tileSubMenu.setShortcut('Ctrl+t')
        self.tileSubMenu.triggered.connect(self.tileWindows)
        self.windowsMenu.addAction(self.tileSubMenu)
        self.windowsMenu.addSeparator()


        self.systemMenu = self.mainMenu.addMenu('&System')
        # add Windows submenu
        self.settingsSubMenu = QAction('Settings', self)
        self.settingsSubMenu.setShortcut('Ctrl+s')
        self.settingsSubMenu.triggered.connect(self.settingsDialog)
        self.systemMenu.addAction(self.settingsSubMenu)


        # subWinList = QMdiArea.subWindowList(mdiArea)
        # for sw in subWinList:
        #     title = '{}'.format(sw.windowTitle)
        #     print(title)
        #     self.winid = QAction(title, self)
        #     self.winid.triggered.connect(sw.setFocus())
        #     self.windowsMenu.addAction(self.winid)

        # self.toolsMenu = self.mainMenu.addMenu('&Tools')
        # self.helpMenu = self.mainMenu.addMenu('&Help')

        self.cw = ChildWidget()

        self.setCentralWidget(self.cw)
        self.resized.connect(self.myResizeFunc)

        self.textEdit = QTextEdit()
        self.textEdit.setEnabled(False)
        self.textEdit.setGeometry(400, 1, 400, 200)
        self.textEdit.move(400, 1)

        self.dock = QDockWidget("Activity Log", self)
        self.dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock)
        self.dock.setWidget(self.textEdit)
        self.textEdit.append('Started.')
        self.center()

    def settingsDialog(self):
        settingsdialog = QDialog()
        settingsdialog.ui = Setting_dialog()
        settingsdialog.ui.setupUi(settingsdialog)

        # connect the two functions
        settingsdialog.ui.cancel.clicked.connect(settingsdialog.close)
        settingsdialog.ui.update.clicked.connect(self.sittingsUpdate)
        settingsdialog.exec_()
        settingsdialog.show()

    def sittingsUpdate(self):
        print('Do settings update here')


    def cascadeWindows(self, event):
        mdiArea.cascadeSubWindows()

    def tileWindows(self, event):
        mdiArea.tileSubWindows()

    def exitWindow(self, event):
        self.close()

    def resizeEvent(self, event):
        self.resized.emit()
        return super(ControlWindow, self).resizeEvent(event)

    def myResizeFunc(self):
        parent_g = self.parent().geometry()

    def contextMenuEvent(self, event):
        cmenu = QMenu(self)
        newAct = cmenu.addAction("New")
        opnAct = cmenu.addAction("Open")
        quitAct = cmenu.addAction("Exit")
        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        if action == quitAct:
            self.close()

    def closeEvent(self, event):
        event.ignore()
        mdiArea.close()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class StQMdiArea(QMdiArea):
    def __init__(self):
        super(StQMdiArea, self).__init__()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def resizeEvent(self, event):
        subWinList = QMdiArea.subWindowList(self)
        # g = self.geometry()
        # for sw in subWinList:
        #     print(sw.windowTitle())
        #     sw.setGeometry(g)
        super(StQMdiArea, self).resizeEvent(event)


class StQLaber(QLabel):
    def __init__(self):
        super(StQLaber, self).__init__()
        self.myName = ''

    def addToWindowsMenu(self, Name):
        global controlWindow
        self.myName = Name
        self.winid = QAction(Name, self)
        self.winid.triggered.connect(self.inFocusWindow)
        controlWindow.windowsMenu.addAction(self.winid)

    def removeFromWindowMenu(self):
        self.winid.setVisible(False)

    def inFocusWindow(self):
        global mdiArea
        self.setEnabled(True)
        self.setWindowState(QtCore.Qt.WindowActive)
        self.setFocus()

    def closeEvent(self, event):
        event.ignore()
        self.setWindowState(QtCore.Qt.WindowMinimized)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Stock Analysis')
        
        # Create the MDI area and set it as the central widget
        self.mdiArea = StQMdiArea()
        self.setCentralWidget(self.mdiArea)
        
        # Create the control window and add it as a subwindow in the MDI area
        self.controlWindow = ControlWindow()
        subWindow = self.mdiArea.addSubWindow(self.controlWindow)
        subWindow.resize(1200, 200)
        self.controlWindow.show()
        
class ChildWidget(QWidget):
    global mainWindow
    
    def __init__(self):
        super(ChildWidget, self).__init__()
        layout = QVBoxLayout()

        self.label1 = QLabel('Enter Stock Symbols: ', self)
        # self.layout.addWidget(self.label1)
        self.label1.move(5, 1)
        self.label1.resize(200, 40)

        self.txtBox = QLineEdit(self)
        self.txtBox.setFocus(True)
        # self.layout.addWidget(self.txtBox)
        self.txtBox.move(205, 1)
        self.txtBox.resize(280, 40)
        self.txtBox.returnPressed.connect(self.genCharts2)

        self.chartbtn = QPushButton('Start Charting', self)
        # self.layout.addWidget(self.chartbtn)
        self.chartbtn.setToolTip('Start charting stocks')
        self.chartbtn.clicked.connect(self.genCharts2)
        self.chartbtn.resize(self.chartbtn.sizeHint())
        self.chartbtn.move(495, 10)

        self.label2 = QLabel("use ',' for multiple symbols", self)
        self.label2.move(650, 1)
        self.label2.resize(200, 40)

        self.setLayout(layout)

    def resizeMe(self):
        parent_g = self.parent().geometry()

    def resizeEvent(self, event):
        #       print('Got resize event')
        self.resizeMe()
        return super(ChildWidget, self).resizeEvent(event)

    def showImage(self, event, filename):
        global imageWinCount

        pixmap = QPixmap(filename)
        if pixmap:
            ql = StQLaber()
            ql.setWindowTitle(filename)
            ql.addToWindowsMenu(filename)
            imagesLabels[imageWinCount] = ql

            imagesLabels[imageWinCount].setPixmap(pixmap)
            subwindows.append(mdiArea.addSubWindow(imagesLabels[imageWinCount]))

            imagesLabels[imageWinCount].show()
            imageWinCount += 1
        else:
            print('No image found')

    def parseLine2List(self, line):
        return list(map(str.strip, line.upper().split(',')))

    def readStockSymb(self):
        global symb
        symb = self.parseLine2List(self.txtBox.text())

    def genCharts2(self, event=None):
        global mdiArea
        global imageWinCount, subwindows, symb, attempt, retry_time, retry_count

        # Clean up old windows and charts
        if mdiArea:
            for w in subwindows:
                w.close()
                imageWinCount -= 1
            subwindows = []

        self.readStockSymb()
        self.parent().textEdit.append('Charting {}'.format(symb))

        if not symb:
            return

        i = 0
        for s in symb:
            i += 1
            attempt = 1
            self.parent().statusBar().showMessage('Collecting data for ' + s)
            self.label2.setText('Collecting data for ' + s + '...')

            while not self.getData(self, s) and attempt < retry_count:
                attempt += 1
                # time.sleep(retry_time)
                QtTest.QTest.qWait(retry_time * 1000)
                self.label2.setText('Retry! Collecting data for ' + s + '...')

            if attempt < retry_count:
                self.parent().statusBar().showMessage('Charting ' + s)
                self.label2.setText('Charting ' + s)
                self.plotData2(self, s)
                # self.parent().statusBar().showMessage('Completed ' + s)
                self.label2.setText('Completed ' + s)
                if i < len(symb):
                    # time.sleep(10)
                    QtTest.QTest.qWait(wait_between_requests * 1000)
                else:
                    break
        self.parent().statusBar().showMessage('Done Charting!')
        self.label2.setText('Done!')

        self.setFocus(True)
        self.txtBox.setFocus(True)

    def getData(self, event, s):
        global data_list
        try:
            # data_list[s] = DataReader(s, data_source, startDate, endDate)
            data_list[s] = yf.download(s,period='2y',progress=False)
            return True

        except RemoteDataError:
            err = 'Remote call failed. Will wait for {0} seconds to retry'.format(retry_time)
            self.parent().textEdit.append('Error {}'.format(err))
            print('Exception : {}'.format(err))
            return False

        # except requests_exceptions:
        #     err = 'Request exception. Will retry ...'
        #     self.parent().textEdit.append('Error {}'.format(err))
        #     return False

    def plotData(self, event, s):
        plt.figure()
        ss = data_list[s]['Adj Close']

        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(s)
        ss.plot().grid(linestyle=':', b=True, which='both', )
        filename = s + '.png'
        plt.savefig(s + filename)
        self.showImage(self, filename)

    def plotData2(self, event, s):
        self.pandas_candlestick_ohlc(self, data_list[s], s, stick=chart_stick_scale)

    def pandas_candlestick_ohlc(self, event, dat, s, stick="day", otherseries=None):
        """
        :param dat: pandas DataFrame object with datetime64 index, and float columns "Open", "High", "Low", and "Close", likely created via DataReader from "yahoo"
        :param stick: A string or number indicating the period of time covered by a single candlestick. Valid string inputs include "day", "week", "month", and "year", ("day" default), and any numeric input indicates the number of trading days included in a period
        :param otherseries: An iterable that will be coerced into a list, containing the columns of dat that hold other series to be plotted as lines

        This will show a Japanese candlestick plot for stock data stored in dat, also plotting other series if passed.
        """
        mondays = WeekdayLocator(MONDAY)  # major ticks on the mondays
        alldays = DayLocator()  # minor ticks on the days
        dayFormatter = DateFormatter('%d')  # e.g., 12

        # Create a new DataFrame which includes OHLC data for each period specified by stick input
        transdat = dat.loc[:, ["Open", "High", "Low", "Close","Volume"]]
        if (type(stick) == str):
            if stick == "day":
                plotdat = transdat
                stick = 1  # Used for plotting
            elif stick in ["week", "month", "year"]:
                if stick == "week":
                    transdat["week"] = pd.to_datetime(transdat.index).map(
                        lambda x: x.isocalendar()[1])  # Identify weeks
                elif stick == "month":
                    transdat["month"] = pd.to_datetime(transdat.index).map(lambda x: x.month)  # Identify months
                transdat["year"] = pd.to_datetime(transdat.index).map(lambda x: x.isocalendar()[0])  # Identify years
                grouped = transdat.groupby(list(set(["year", stick])))  # Group by year and other appropriate variable
                plotdat = pd.DataFrame({"Open": [], "High": [], "Low": [],
                                        "Close": [],"Volume":[]})  # Create empty data frame containing what will be plotted
                for name, group in grouped:
                    new_row = pd.DataFrame({"Open": [group.iloc[0, 0]],
                                            "High": [max(group.High)],
                                            "Low": [min(group.Low)],
                                            "Close": [group.iloc[-1, 3]],
                                            "Volume":[group.iloc[-1, 4]]},
                                        index=[group.index[0]])
                    if plotdat.empty:
                        plotdat = new_row
                    else:
                        plotdat = pd.concat([plotdat, new_row])
                if stick == "week":
                    stick = 5
                elif stick == "month":
                    stick = 30
                elif stick == "year":
                    stick = 365

        elif (type(stick) == int and stick >= 1):
            transdat["stick"] = [np.floor(i / stick) for i in range(len(transdat.index))]
            grouped = transdat.groupby("stick")
            plotdat = pd.DataFrame(
                {"Open": [], "High": [], "Low": [],
                 "Close": [],"Volume":[]})  # Create empty data frame containing what will be plotted
            for name, group in grouped:
                plotdat = plotdat.append(pd.DataFrame({"Open": group.iloc[0, 0],
                                                       "High": max(group.High),
                                                       "Low": min(group.Low),
                                                       "Close": group.iloc[-1, 3],
                                                       "Volume": group.iloc[-1, 4]},
                                                      index=[group.index[0]]))
                

        else:
            raise ValueError(
                'Valid inputs to argument "stick" include the strings "day", "week", "month", "year", or a positive integer')

        # Set plot parameters, including the axis object ax used for plotting
        # fig, ax = plt.subplots(
        #     figsize=(16, 9)
        # )
        # fig.subplots_adjust(bottom=0.2)
        # if plotdat.index[-1] - plotdat.index[0] < pd.Timedelta('350 days'):
        #     weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
        #     ax.xaxis.set_major_locator(mondays)
        #     ax.xaxis.set_minor_locator(alldays)
        # else:
        #     weekFormatter = DateFormatter('%b %d, %Y')
        # ax.xaxis.set_major_formatter(weekFormatter)

        # ax.grid(True)

        # candlestick_ohlc.plot(transdat["week"],type='candle')
        # Create the candelstick chart
        # candlestick_ohlc(ax, list(
        #     zip(list(dd.date2num(plotdat.index.tolist())), plotdat["Open"].tolist(), plotdat["High"].tolist(),
        #         plotdat["Low"].tolist(), plotdat["Close"].tolist())),
        #                  colorup="black", colordown="red", width=stick)
        
                
        style = candlestick_ohlc.make_mpf_style(marketcolors=candlestick_ohlc.make_marketcolors(up="r", down="#0000CC",inherit=True),
                           gridcolor="gray", gridstyle="--", gridaxis="both") 
        
        print(plotdat)
        
        fig2, ax = candlestick_ohlc.plot(type='candle',data=plotdat,mav=(20,40,50,200),
                                     style=style,volume=True,tight_layout=True,returnfig=True,figsize =(16,9), axtitle=f"{s} Stock Chart")

        # Plot other series (such as moving averages) as lines
        if otherseries != None:
            if type(otherseries) != list:
                otherseries = [otherseries]
            dat.loc[:, otherseries].plot(ax=ax, lw=1.3, grid=True)

        # ax.xaxis_date()
        # ax.autoscale_view()
        # plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
        


        # plt.xlabel('Date')
        # plt.ylabel('Price')
        # plt.title(s)        
        
        # Create and Customize a legend
        # ax.legend()
        # ax[0].legend([None]*(len(added_plots)+2))
        # handles = axes[0].get_legend().legendHandles
        # axes[0].legend(handles=handles[2:],labels=list(plotdat.columns[4:]))
        
        filename = s + '.png'
        plt.savefig(filename)

        self.showImage(self, filename)


def main():
    global mdiArea, controlWindow
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('dataicon.png'))
    
    mainWindow = MainWindow()
    
    # Maximize the main window
    mainWindow.showMaximized()
    mdiArea = mainWindow.mdiArea  # Assign the mdiArea from MainWindow to the global mdiArea

    # Show the main window
    mainWindow.show()

    controlWindow = ControlWindow()

    mdiArea.addSubWindow(controlWindow).resize(1200, 200)
    mdiArea.setWindowTitle('Stock Analysis')
    mdiArea.show()
    sys.exit(app.exec_())


main()
