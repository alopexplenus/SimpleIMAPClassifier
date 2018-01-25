"""
Finally, predicting!
"""
import numpy as np
import pandas as pd
import configparser
import pickle
from mailworker import  MailWorker

config = configparser.ConfigParser()
config.read('config.ini')


if __name__ == "__main__":
    df = pd.read_csv(config['DATA']['recent_labeled_file'], sep=';', index_col=False)
    print(df.shape)
    df.fillna(0, inplace=True)
    answered = np.asarray(df.Answered)[:, None]
    uids = np.asarray(df.UID)[:, None]
    print(uids)
    df.drop('Answered', axis=1, inplace=True)
    df_features = df.to_dict(orient='records')
    vec = pickle.load(open('vectorizer.p', 'rb'))
    features = vec.transform(df_features).toarray()

    #print(labels_test)
    clf = pickle.load(open('model.p', 'rb'))

#look what it actually predicts
    predictions = clf.predict_proba(features)
    #np.append(predictions, labels_test)
    print(predictions.shape)
    predictions_with_uid = np.hstack((predictions, answered, uids))
    print(predictions_with_uid)
    mw = MailWorker()
    for prediction in predictions_with_uid:
        if prediction[0] < 0.9:
            print(prediction[3])
            mw.storeflag(str(int(prediction[3])))
