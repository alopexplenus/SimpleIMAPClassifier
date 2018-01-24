"""
module to read out messages into csv
"""
from imaplib import IMAP4_SSL
from datetime import date, timedelta
from time import strftime
import email
import dateutil.parser
import numpy as np
import pandas as pd
import configparser
import argparse
from mailworker import  MailWorker

config = configparser.ConfigParser()
config.read('config.ini')


def usefulHeaders():
    return [
        'Answered',
        'UID',
        'Auto-Submitted',# whether its an auto-reply
        'Content-Language',
        'Date',
        'From',
        'To',
        'CC',
        'Cc',
        'Importance',
        'NewSubject',
        'NewMessageText',
        ]





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='specify number of email data volume')
    parser.add_argument('volume_number', type=int, nargs='?', help='specify the data volume number')
    args = parser.parse_args()
    if args.volume_number == None:
        args.volume_number = 1
    print("VOLUME NUMBER: ", int(args.volume_number))
    mw = MailWorker()
    data, answereddata = mw.get_message_id_list(int(args.volume_number))
    mails = mw.fetch(data, answereddata)
    mw.mailclose()
    print(len(mails), "mails in dataset")
    mydata = np.empty((len(mails), len(usefulHeaders())), dtype='object')
    row = 0
    for m in mails:
        col = 0
        for k in usefulHeaders():
            mydata[row][col] = m[k]
            col += 1
        row += 1
    print("populated ndarray")

    MyDataFrame = pd.DataFrame(mydata, columns=usefulHeaders(), dtype=str)
    if args.volume_number == 1:
        MyDataFrame.to_csv(config['DATA']['recent_file'], sep=';', index=False)
    elif args.volume_number == 2:
        MyDataFrame.to_csv(config['DATA']['primary_data_file'], sep=';', index=False)
    else:
        MyDataFrame.to_csv(config['DATA']['primary_data_file'], sep=';', mode='a', header=False, index=False)
