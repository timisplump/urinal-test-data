import pandas as pd
import basicAnalysis

from sklearn import datasets
from sklearn import metrics
from sklearn.naive_bayes import GaussianNB, MultinomialNB


def bayesianModel(filename):
    bigData = pd.read_csv(filename)
    indices = bigData['index'].values.tolist()
    priors = bigData[['age', 'height']].values.tolist()
    for row in range(len(bigData)):
        for i in range(7):
            if 'empty' in bigData.iloc[row]['urinal' + str(i)]:
                priors[row].append(1)
            else:
                priors[row].append(0)
    #print(priors)
    #urinalGroups = bigData.groupby(['urinal0', 'urinal1', 'urinal2', 'urinal3',	'urinal4', 'urinal5', 'urinal6'])['index']
    #print(urinalGroups.groups)

    #groups = list(urinalGroups.groups.keys())

    #a = urinalGroups.groups[groups[0]]
    #b = bigData.iloc[a[0]]


    model = GaussianNB()
    model.fit(priors, indices)
    print(priors[:10])
    print(indices[:10])
    predicted = model.predict(priors)
    print(expected[:10])
    print(metrics.classification_report(indices, predicted))
    i = 0
    for index in range(len(predicted)):
        if priors[index][predicted[index]+2] ==0:
            i+= 1
bayesianModel