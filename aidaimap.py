"""
module to read out messages per IMAP
"""
from imaplib import IMAP4_SSL
from datetime import date, timedelta, datetime
from time import mktime
from time import strptime
import email
import dateutil.parser
from pylab import plot_date, show, xticks, date2num
from pylab import figure, hist, num2date
from matplotlib.dates import DateFormatter

from visualization import diurnalplot
from visualization import dailyDistributioPlot


import configparser
config = configparser.ConfigParser()
config.read('config.ini')


# In[99]:

def getHeaders():
    """ retrieve the headers of the emails
        from d days ago until now """
    fulldata = []
    # imap connection
    mail = IMAP4_SSL(config['SERVER']['imap_address'])
    mail.login(config['SERVER']['login'], config['SERVER']['password'])
    print('selecting folder ', config['DATA']['folder'])
    typ = mail.select(config['DATA']['folder'])
    print('Response code:', typ)
    typ, data = mail.list()
    print('list():')
    print(data)
    print('retrieving the uids')
    interval = (date.today() - timedelta(int(config['DATA']['days']))).strftime("%d-%b-%Y")
    result, data = mail.search(None, '(SENTSINCE {date})'.format(date=interval))
    print(len(data[0]), 'Email numbers fetched.')
    print('retrieving the headers')
    for num in data[0].split():
        typ, mdata = mail.fetch(num, '(RFC822)')
        for response_part in mdata:
            if isinstance(response_part, tuple):
                part = response_part[1].decode('utf-8')
                msg = email.message_from_string(part)
                #print(msg.keys())
                #print(msg['Date'])
        fulldata.append(msg)
    print(len(fulldata), 'headers fetched.')
    mail.close()
headers = getHeaders()
print(headers[0].keys())

xday, ytime = diurnalplot(headers)
dailyDistributioPlot(ytime)
print(len(xday), 'Emails analysed.')
show()
