"""
numeric labelings instead of string data
"""
# pylint: disable=line-too-long
from sklearn import preprocessing

if __name__ == "__main__":
# labels to numbers
    for toField in ['To1', 'To2', 'To3', 'To4', 'To5', 'To6', 'CC1', 'CC2', 'CC3', 'CC4', 'CC5', 'CC6', 'From', 'Content-Language', 'Auto-Submitted']:
        le = preprocessing.LabelEncoder()
        print(toField)
        le.fit(df[toField])
        print("FITS")
        df[toField] = le.transform(df[toField])
