"""
Finally, predicting!
"""
import numpy as np
import pandas as pd
import configparser
import pickle
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

config = configparser.ConfigParser()
config.read('config.ini')


if __name__ == "__main__":
    df = pd.read_csv(config['DATA']['recent_labeled_file'], sep=';')
    print(df.describe())
    df.fillna(0, inplace=True)
    uid_list = np.asarray(df.UID)
    df.drop('Answered', axis=1)
    df_features = df.to_dict(orient='records')
    vec = DictVectorizer()
    features = vec.fit_transform(df_features).toarray()

    #print(labels_test)
    clf = pickle.load(open('model.p', 'rb'))

#look what it actually predicts
    predictions = clf.predict_proba(features)
    #np.append(predictions, labels_test)
    print(predictions.shape)
    predictions_with_uid = np.hstack((predictions, uid_list))
