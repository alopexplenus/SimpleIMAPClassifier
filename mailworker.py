"""
module for IMAP
"""
from imaplib import IMAP4_SSL
from datetime import date, timedelta
from time import strftime
import email
import dateutil.parser
import numpy as np
import pandas as pd
import re
import configparser

config = configparser.ConfigParser()
config.read('config.ini')




class MailWorker():
    def __init__(self):
        """ retrieve the headers of the emails
            from d days ago until now """
#mail.store(uid, '+FLAGS', '(\\Seen)')

        # imap connection
        self.mail = IMAP4_SSL(config['SERVER']['imap_address'])
        self.mail.login(config['SERVER']['login'], config['SERVER']['password'])
        print('selecting folder ', config['DATA']['folder'])
        typ = self.mail.select(config['DATA']['folder'])
        print('Response code:', typ)
        #uids = self.mail.uid('SEARCH', 'ALL')[1][0].split()
        #print(uids)
        #self.storeflag(uids[-1])

    def storeflag(self, uid):
        self.mail.uid('STORE', uid, '+FLAGS', r'\Flagged')

    def get_message_id_list(self, volume):
        interval = timedelta(int(config['DATA']['days']))
        sentsince = (date.today() - volume*interval).strftime("%d-%b-%Y")
        condition = 'SENTSINCE {date}'.format(date=sentsince)
        if volume > 1:
            sentbefore = (date.today() - (volume-1)*interval).strftime("%d-%b-%Y")
            condition += ' SENTBEFORE {date}'.format(date=sentbefore)
        data = self.mail.uid('SEARCH', '('+condition+')')[1][0].split()
        answereddata = self.mail.uid('SEARCH', '(ANSWERED '+condition+')')[1][0].split()
        for uid in answereddata:
            self.storeflag(uid)
        return data, answereddata

    def listHeaders(self):
        return [
            'Precedence',
            'list-Id',
            'list-Post',
            'list-help',
            'list-unsubscribe',
            'list-owner',
            ]

    def fetch(self, data, answereddata):
        fulldata = []
        REPLY_SEPARATOR = "From:"
        print(len(data), 'Email numbers fetched.')
        print(len(answereddata), 'Emails were answered.')
        #print(data)
        for num in data:
            typ, mdata = self.mail.uid('fetch', num, '(RFC822)')
            if typ == 'NO':
                print(num, typ)
                continue
            for response_part in mdata:
                if isinstance(response_part, tuple):
                    try:
                        part = response_part[1].decode('utf-8')
                    except:
                        print("COULD NOT DECODE MESSAGE")
                        continue
                    msg = email.message_from_string(part)
            for lHeader in self.listHeaders():
                if msg[lHeader] != None:
                    continue
            for anum in answereddata:
                if anum == num:
                    msg['Answered'] = 1
            text = ''
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        text = part.get_payload()
            else:
                try:
                    text = msg.get_payload(None, True).decode('utf-8').split(REPLY_SEPARATOR)[0]
                except:
                    text = str(msg.get_payload(None, True)).split(REPLY_SEPARATOR)[0]
            msg['NewSubject'] = email.header.make_header(email.header.decode_header(msg['Subject']))
            msg['UID'] = num
# FILTER OUT UNNEEDED CALENDAR ITEMS AND NOTIFICATIONS
            if text.find('path=/calendar/item') > 0:
                continue
            if msg['From'].find('info@interpont.com') > 0:
                continue
            msg['NewMessageText'] = self.cleanhtml(text)
            #print(msg['NewSubject'])
            #msg.pop('Subject', None) # drop it for good
            fulldata.append(msg)
        return fulldata

    def cleanhtml(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleanr_curlybraces = re.compile('{.*?}')
        cleantext = re.sub(cleanr, ' ', raw_html.replace('\n', ' ').replace('\r', '').replace(';', ''))
        cleantext = re.sub(cleanr_curlybraces, '', cleantext)
        return cleantext.strip()

    def mailclose(self):
        self.mail.close()
