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


def getData(s):
    global data_list
    try:
        data_list[s] = DataReader(s, 'yahoo', startDate, endDate)
        return True
    except RemoteDataError:
        print('Exception : Remote call failed. Will wait for {0} seconds to retry'.format(retry_time))
        return False


def plotData(s):
    plt.figure()
    ss = data_list[s]['Adj Close']

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(s)
    ss.plot().grid(linestyle=':', b=True, which='both', )
    plt.savefig(s+'.png')
    print("Plotted " + s)


try:
    i = 0
    for s in symb:
        i += 1
        attempt = 1
        while not getData(s) and attempt < retry_count:
            attempt = +1
            time.sleep(retry_time)

        if attempt < retry_count:
            plotData(s)
            print('Completed ' + s)
            if i < len(symb):
                time.sleep(10)
            else:
                break

    #plt.show()

except KeyboardInterrupt:
    print('Key Interrupt!!')
except Exception as e:
    print('Exception :{0}'.format(e.__cause__))
