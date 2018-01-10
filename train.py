"""
Training
"""
import numpy as np
import pandas as pd
import configparser
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

config = configparser.ConfigParser()
config.read('config.ini')

if __name__ == "__main__":
    df = pd.read_csv(config['DATA']['labeled_data_file'], sep=';')
    print(df.describe())
    #print(df.head())
    df.fillna(0, inplace=True)
    answered = np.asarray(df.Answered)
    df.drop('Answered', axis=1)
    df_features = df.to_dict(orient='records')
    vec = DictVectorizer()
    features = vec.fit_transform(df_features).toarray()
    features_train, features_test, labels_train, labels_test = train_test_split(features, answered, test_size=0.20, random_state=32)
    print(labels_test)
    clf = RandomForestClassifier()
    clf.fit(features_train, labels_train)

# compute accuracy using test data
    acc_test = clf.score(features_test, labels_test)

    print("Test Accuracy:", acc_test)
