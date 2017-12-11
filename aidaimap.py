"""
module to read out messages per IMAP
"""
from imaplib import IMAP4_SSL
from datetime import date, timedelta
from time import strftime
import email
import dateutil.parser
from pylab import show

from visualization import diurnalplot
from visualization import dailydistributioplot


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
    # getting folder structure
    #typ, data = mail.list()
    #print(data)
    interval = (date.today() - timedelta(int(config['DATA']['days']))).strftime("%d-%b-%Y")
    result, data = mail.search(None, '(SENTSINCE {date})'.format(date=interval))
    result, answereddata = mail.search(None, '(ANSWERED SENTSINCE {date})'.format(date=interval))
    print(len(data[0]), 'Email numbers fetched.')
    print(len(answereddata[0]), 'Emails were answered.')
    for num in data[0].split():
        typ, mdata = mail.fetch(num, '(RFC822)')
        for response_part in mdata:
            if isinstance(response_part, tuple):
                try:
                    part = response_part[1].decode('utf-8')
                except:
                    print("COULD NOT DECODE MESSAGE")
                    continue
                msg = email.message_from_string(part)
                #print(msg.keys())
                print(msg['Date'])
        for anum in answereddata[0].split():
            if anum == num:
                msg['Answered'] = 1
        fulldata.append(msg)
        print(msg['Date'], msg['From'])
        print(email.header.make_header(email.header.decode_header(msg['Subject'])))
    mail.close()
    return fulldata
headers = getHeaders()

xday, ytime = diurnalplot(headers)
dailydistributioplot(ytime)
print(len(xday), 'Emails analysed.')
show()
