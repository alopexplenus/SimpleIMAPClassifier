"""
this is where i choose and extract features from my emails

"""
# pylint: disable=line-too-long
import sys
import pandas as pd
import configparser
import requests
import re #may the force of regex be with you
from sklearn import preprocessing

config = configparser.ConfigParser()
config.read('config.ini')


def read_contacts_from_JSON():
    login_data = {'mail':config['CRM']['mail'], 'password':config['CRM']['password']}
    r = requests.post(config['CRM']['own_contacts_url'], data=login_data)
    jsondata = r.json()
    print(len(jsondata), " CONTACTS FETCHED")
    print(jsondata[100], " NUMBER 100")




def message_features():
    """
        just a list of wanted features
    """
    return [
        'Dom',
        'Dow',
        'IsCalendarEvent',
        'IsInHTML',
        'sender_email', #  later be labelized with sklearn.preprocessing.LabelEncoder
        'InternalSenderPosition', # from CRM
        'ExternalSenderPosition', # from CRM
        'ClientId', # from CRM
        'SenderContactStatus', # data from CRM
        'SenderReceivesFinancialData', # data from CRM
        'NumberOfAttachments',
        'NumberOfWordAttachments',
        'NumberOfExcelAttachments',
        'NumberOfPdfAttachments',
        'NumberOfPptAttachments',
        'SenderTLD', # will later be labelized with sklearn.preprocessing.LabelEncoder
        'EstimatedLanguage',
        'To1',
        'To2',
        'To3',
        'To4',
        'To5',
        'To6',
        'IsForwarded',
        'NumberOfReplies',
        'IsReplyingToMe',
        'IAmInThread',
        'IAmInCC', # 0 for recepient, 1 for CC, 2 for BCC
    ]

if __name__ == "__main__":
    print("LOADING DATA")
    filename = sys.argv.pop()
    df = pd.DataFrame.from_csv(config['DATA']['primary_data_file'], sep=';')

    usefulHeaders = [
        'isList',
        #'Accept-Language',
        'Answered',
        'Auto-Submitted',# whether its an auto-reply
        'Content-Language',
        'Date',
        'From',
        'To1',
        'To2',
        'To3',
        'To4',
        'To5',
        'To6',
        'Importance',
        'NewSubject',
        #'Thread-Topic',
        ]


    df.assign(isList=pd.Series(range(len(df))))
    df.assign(To1=pd.Series(range(len(df))))
    df.assign(To2=pd.Series(range(len(df))))
    df.assign(To3=pd.Series(range(len(df))))
    df.assign(To4=pd.Series(range(len(df))))
    df.assign(To5=pd.Series(range(len(df))))
    df.assign(To6=pd.Series(range(len(df))))

    df['CC'].fillna(df['Cc'], inplace=True)
    del df['Cc']
    df['X-Originating-IP'].fillna(df['x-originating-ip'], inplace=True)
    del df['x-originating-ip']

    allmails = list()
    for i in range(len(df)):
        if df["Precedence"][i] == "bulk":
            df.loc[i, 'isList'] = 1
        df.loc[i, "From"] = re.search(r'[\w\.-]+@[\w\.-]+', df["From"][i]).group(0)

        toPeople = list(re.findall(r'[\w\.-]+@[\w\.-]+', df["To"][i]+', '+df["CC"][i]))
        allmails = allmails + toPeople

        for toField in ['To1', 'To2', 'To3', 'To4', 'To5', 'To6']:
            try:
                addr = toPeople.pop()
                df.loc[i, toField] = addr
            except:
                df.loc[i, toField] = "..."

        #print(df["From"][i])
    for columnName in list(df.columns.values):
        if columnName[:5] == "List-":
            for i in range(len(df)):
                if df[columnName][i] != "None":
                    #print(df[columnName][i])
                    df.loc[i, 'isList'] = 1
            df.drop(columnName, axis=1, inplace=True)
        elif not columnName in usefulHeaders:
            #print("DROPPING ", columnName)
            df.drop(columnName, axis=1, inplace=True)
    #print(df['isList'])
    for i in range(len(df)):
        if df["isList"][i] == 11:
            print("From: ", df['From'][i]) # let us see all them spammers
    #print(df.describe())
df.to_csv(config['DATA']['processed_data_file'], sep=';')


# labels to numbers
for toField in ['From', 'Content-Language', 'Auto-Submitted']:
    le = preprocessing.LabelEncoder()
    print(toField)
    le.fit(df[toField])
    print("FITS")
    df[toField] = le.transform(df[toField])

df.to_csv(config['DATA']['labeled_data_file'], sep=';')

#read_contacts_from_JSON()
