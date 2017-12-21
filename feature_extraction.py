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





if __name__ == "__main__":
    print("LOADING DATA")
    filename = sys.argv.pop()
    df = pd.DataFrame.from_csv(config['DATA']['primary_data_file'], sep=';')

    usefulHeaders = [
        'isList',
        'Answered',
        #'Auto-Submitted',# whether its an auto-reply
        'Content-Language',
        'Date',
        'From',
        'To',
        'CC',
        #'Importance',
        'NewSubject',
        'NewMessageText',
        ]


    df.assign(isList=pd.Series(range(len(df))))
    df.assign(weekday=pd.Series(range(len(df))))

    try:
        df['CC'].fillna(df['Cc'], inplace=True)
        del df['Cc']
    except:
        print("Apparantly no Cc headers found in dataframe")
    try:
        df['X-Originating-IP'].fillna(df['x-originating-ip'], inplace=True)
        del df['x-originating-ip']
    except:
        print("Apparantly no x-originating-ip headers found in dataframe")

    for columnName in list(df.columns.values):
        if columnName[:5] == "List-":
            for i in range(len(df)):
                if df[columnName][i] != "None":
                    #print(df[columnName][i])
                    df.loc[i, 'isList'] = 1
            df.drop(columnName, axis=1, inplace=True)
        elif not columnName in usefulHeaders:
            df.drop(columnName, axis=1, inplace=True)

    myDictIsVeryBig = dict()
    myContacts = dict()

# CREATING DICTIONARIES
    for i in range(len(df)):
        NewSubject = df['NewSubject'][i]
        NewMessageText = df['NewMessageText'][i]
        SubjectWords = []
        try:
            #NS = re.sub(r'[+\-,.<>()%$:|/#_0-9!]', ' ', NewSubject)
            SubjectWords = re.findall(r'\b\w{3,33}\b', NewSubject)
        except:
            print("subject regepx failed: ", NewSubject)

        for word in SubjectWords:
            #print(word)
            if word in myDictIsVeryBig:
                myDictIsVeryBig[word] += 1
            else:
                myDictIsVeryBig[word] = 1
                df.assign(word=pd.Series(range(len(df))))
                df.loc[i, word] = 1

        BodyWords = []
        try:
            BodyWords = re.findall(r'\b\w{4,33}\b', NewMessageText)
        except:
            print("body regepx failed: ", NewMessageText)

        for word in BodyWords:
            #print(word)
            if word in myDictIsVeryBig:
                myDictIsVeryBig[word] += 1
                if myDictIsVeryBig[word] == 100:
                    df.drop(word, axis=1, inplace=True)
                if myDictIsVeryBig[word] < 100:
                    df.loc[i, word] = 1
            else:
                myDictIsVeryBig[word] = 1
                df.assign(word=pd.Series(range(len(df))))
                df.loc[i, word] = 1

        toPeople = list(re.findall(r'[\w\.-]+@[\w\.-]+', df["To"][i]+', '+df["CC"][i]))
        for address in toPeople:
            if address in myContacts:
                myContacts[address] += 1
            else:
                myContacts[address] = 1
                df.assign(address=pd.Series(range(len(df))))
            df.loc[i, address] = 1

    print(sorted(myDictIsVeryBig.items(), key=lambda x: x[1]))

# CUTTING TOO RARE WORDS
    for word in myDictIsVeryBig:
        if myDictIsVeryBig[word] == 1:
            df.drop(word, axis=1, inplace=True)

# WORKING ON VALUES

    for i in range(len(df)):
        try:
            if df["Precedence"][i] == "bulk":
                df.loc[i, 'isList'] = 1
        except:
            print("no precedence header in df")
        try:
            df.loc[i, "From"] = re.search(r'[\w\.-]+@[\w\.-]+', df["From"][i]).group(0)
        except:
            df.loc[i, "From"] = 'n/a'

        if df["Answered"][i] != "1":
            df.loc[i, 'Answered'] = 0
        try:
            df.loc[i, 'Date'] = str(df['Date'][i][:3])
        except:
            print("could not parse date "+str(df['Date'][i]))
            df.loc[i, 'Date'] = 'n/a'



    print("WRITING PROCESSED FILE")
    df.to_csv(config['DATA']['processed_data_file'], sep=';')


# labels to numbers
    for toField in ['From', 'Content-Language', 'Date']:
        le = preprocessing.LabelEncoder()
        print("FITTING: ", toField)
        le.fit(df[toField])
        df[toField] = le.transform(df[toField])

    df.drop("To", axis=1, inplace=True)
    df.drop("CC", axis=1, inplace=True)
    df.drop("NewSubject", axis=1, inplace=True)
    df.drop("NewMessageText", axis=1, inplace=True)
    print("WRITING LABELED FILE")
    df.to_csv(config['DATA']['labeled_data_file'], sep=';')
