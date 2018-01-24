#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Developer : Al Sabawi
Name : stocks.py
Date : 01/23/2018

"""

import time
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator, \
    DayLocator, MONDAY
from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as dd
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
                self.plotData2(self,s)
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


    def plotData2(self,event,s):
        self.pandas_candlestick_ohlc(self,data_list[s],s)

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
        transdat = dat.loc[:, ["Open", "High", "Low", "Close"]]
        if (type(stick) == str):
            if stick == "day":
                plotdat = transdat
                stick = 1  # Used for plotting
            elif stick in ["week", "month", "year"]:
                if stick == "week":
                    transdat["week"] = pd.to_datetime(transdat.index).map(lambda x: x.isocalendar()[1])  # Identify weeks
                elif stick == "month":
                    transdat["month"] = pd.to_datetime(transdat.index).map(lambda x: x.month)  # Identify months
                transdat["year"] = pd.to_datetime(transdat.index).map(lambda x: x.isocalendar()[0])  # Identify years
                grouped = transdat.groupby(list(set(["year", stick])))  # Group by year and other appropriate variable
                plotdat = pd.DataFrame({"Open": [], "High": [], "Low": [],
                                        "Close": []})  # Create empty data frame containing what will be plotted
                for name, group in grouped:
                    plotdat = plotdat.append(pd.DataFrame({"Open": group.iloc[0, 0],
                                                           "High": max(group.High),
                                                           "Low": min(group.Low),
                                                           "Close": group.iloc[-1, 3]},
                                                          index=[group.index[0]]))
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
                {"Open": [], "High": [], "Low": [], "Close": []})  # Create empty data frame containing what will be plotted
            for name, group in grouped:
                plotdat = plotdat.append(pd.DataFrame({"Open": group.iloc[0, 0],
                                                       "High": max(group.High),
                                                       "Low": min(group.Low),
                                                       "Close": group.iloc[-1, 3]},
                                                      index=[group.index[0]]))

        else:
            raise ValueError(
                'Valid inputs to argument "stick" include the strings "day", "week", "month", "year", or a positive integer')

        # Set plot parameters, including the axis object ax used for plotting
        fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.2)
        if plotdat.index[-1] - plotdat.index[0] < pd.Timedelta('730 days'):
            weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
            ax.xaxis.set_major_locator(mondays)
            ax.xaxis.set_minor_locator(alldays)
        else:
            weekFormatter = DateFormatter('%b %d, %Y')
        ax.xaxis.set_major_formatter(weekFormatter)

        ax.grid(True)

        # Create the candelstick chart
        candlestick_ohlc(ax, list(
            zip(list(dd.date2num(plotdat.index.tolist())), plotdat["Open"].tolist(), plotdat["High"].tolist(),
                plotdat["Low"].tolist(), plotdat["Close"].tolist())),
                         colorup="black", colordown="red", width=stick * .4)

        # Plot other series (such as moving averages) as lines
        if otherseries != None:
            if type(otherseries) != list:
                otherseries = [otherseries]
            dat.loc[:, otherseries].plot(ax=ax, lw=1.3, grid=True)

        ax.xaxis_date()
        ax.autoscale_view()
        plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(s)

        plt.savefig(s + '.png')
        #plt.show()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = mainWindow()
    sys.exit(app.exec_())