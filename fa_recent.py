"""
extract features from my emails for prediction
"""
# pylint: disable=line-too-long
import sys
import pandas as pd
import configparser
import requests
import pickle
import re #may the force of regex be with you
from sklearn import preprocessing
from imaptocsv import usefulHeaders

config = configparser.ConfigParser()
config.read('config.ini')


if __name__ == "__main__":
    print("LOADING DATA")
    filename = sys.argv.pop()
    df = pd.read_csv(config['DATA']['recent_file'], sep=';', index_col=False)
    df_train = pd.read_csv(config['DATA']['labeled_data_file'], sep=';', index_col=False)

    df.assign(weekday=pd.Series(range(len(df))))

    try:
        df['CC'].fillna(df['Cc'], inplace=True)
        del df['Cc']
    except:
        print("Apparantly no Cc headers found in dataframe")

    for columnName in list(df.columns.values):
        if not columnName in usefulHeaders():
            df.drop(columnName, axis=1, inplace=True)

# adding column names like in training dataset
    counter = 0
    for columnName in list(df_train.columns):
        counter += 1
        try:
            df.assign(columnName=np.zeroes(range(len(df))))
            df[columnName].fillna(0, inplace=True)
        except:
            print(columnName, " apparently already in df")
    print(counter, "columns in train dataset")
    print(df.shape)
    print(len(list(df.columns.values)))


# CREATING DICTIONARIES
    for i in range(len(df)):
        NewSubject = str(df['NewSubject'][i]).lower()
        NewMessageText = str(df['NewMessageText'][i]).lower()
        SubjectWords = []
        try:
            SubjectWords = re.findall(r'\b\w{3,15}\b', str(NewSubject))
        except:
            print("subject regepx failed: ", NewSubject)

        for word in SubjectWords:
            #print(word)
            columnName = word+'_s'
            try:
                df.loc[i, columnName] = 1
            except:
                print(columnName, " not found in dataframe")

        BodyWords = []
        try:
            BodyWords = re.findall(r'\b[^\d \t+_/&;-=]{4,15}\b', str(NewMessageText))
        except:
            print("body regepx failed: ", NewMessageText)

        wc = dict()
        for word in BodyWords:
            if word in wc:
                wc[word] += 1
            else:
                wc[word] = 1
            columnName = word+'_b'
            try:
                df.loc[i, columnName] = wc[word]
            except:
                print(columnName, " not found in dataframe")

        toPeople = list(re.findall(r'[\w\.-]+@[\w\.-]+', str(df["To"][i])+', '+str(df["CC"][i])))
        for address in toPeople:
            try:
                df.loc[i, address] = 1
            except:
                print(address, " not found in dataframe")

# removing old TO column
    df.drop("To", axis=1, inplace=True)

# WORKING ON VALUES
    for i in range(len(df)):
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
    df.to_csv(config['DATA']['recent_processed_file'], sep=';')


# labeling
    for toField in ['From', 'Content-Language', 'Date']:
        encoder = pickle.load(open(toField+"-Encoder.p", "rb"))
        for i in range(len(df)):# Это ебаный колхоз, надо сделать нормально
            try:
                df.loc[i, toField] = encoder.transform([df[toField][i]])[0]
            except:
                print("could not find ", df[toField][i], "in label encoder")
                df.loc[i, toField] = 0
    df.drop("CC", axis=1, inplace=True)
    df.drop("NewSubject", axis=1, inplace=True)
    df.drop("NewMessageText", axis=1, inplace=True)
    print("WRITING LABELED FILE")
    df.to_csv(config['DATA']['recent_labeled_file'], sep=';')
