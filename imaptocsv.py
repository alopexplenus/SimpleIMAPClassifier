"""
module to read out messages per IMAP
"""
from imaplib import IMAP4_SSL
from datetime import date, timedelta
from time import strftime
import email
import dateutil.parser
import numpy as np
import pandas as pd



import configparser
config = configparser.ConfigParser()
config.read('config.ini')


# In[99]:

def getHeaders():
    """ retrieve the headers of the emails
        from d days ago until now """
    fulldata = []
    allkeys = set([])
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
    print(len(data[0].split()), 'Email numbers fetched.')
    print(len(answereddata[0].split()), 'Emails were answered.')
    for num in data[0].split():
        #print("message # ", num)
        typ, mdata = mail.fetch(num, '(RFC822)')
        for response_part in mdata:
            if isinstance(response_part, tuple):
                try:
                    part = response_part[1].decode('utf-8')
                except:
                    print("COULD NOT DECODE MESSAGE")
                    continue
                msg = email.message_from_string(part)
                #print(msg['Date'])
        for anum in answereddata[0].split():
            if anum == num:
                msg['Answered'] = 1
        fulldata.append(msg)
        #print("Fulldata len ", len(fulldata))
        msg['NewSubject'] = email.header.make_header(email.header.decode_header(msg['Subject']))
        #print(msg['NewSubject'])
        #msg.pop('Subject', None) # drop it for good
        keys = msg.keys()
        for key in keys:
            if key == "Subject":
                continue
            allkeys.add(key)
        #print(len(allkeys))
        #print(email.header.make_header(email.header.decode_header(msg['Subject'])))
    mail.close()
    print(allkeys)
    return fulldata, allkeys

mails, allkeys = getHeaders()
print(len(mails), "mails in dataset")
mydata = np.empty((len(mails), len(allkeys)), dtype='object')
row = 0
for m in mails:
    col = 0
    for k in allkeys:
        mydata[row][col] = m[k]
        col += 1
    row += 1
#print(mydata[0])
#print(mydata[1])
#print(mydata[11])
#np.savetxt("mailheaders.csv", mydata, delimiter=";")

MyDataFrame = pd.DataFrame(mydata, columns=allkeys, dtype=str)
MyDataFrame.to_csv(config['DATA']['primary_data_file'], sep=';')
