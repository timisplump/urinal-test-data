import pandas as pd
import basicAnalysis
import model_data
import bayesianModel
import lynchHardcodedModel

from sklearn import datasets
from sklearn import metrics
from sklearn.naive_bayes import GaussianNB, MultinomialNB


def addBayesPrediction(dataFrame):
    model = bayesianModel.bayesianModel(dataFrame)
    priors = dataFrame[['age', 'height']].values.tolist()
    for row in range(len(dataFrame)):
        for i in range(7):
            if 'empty' in dataFrame.iloc[row]['urinal' + str(i)]:
                priors[row].append(1)
            else:
                priors[row].append(0)
    predictions = model.predict(priors)

    dataFrame['bayesianPrediction'] = predictions
    return dataFrame

def addLynchHardcodedPrediction(dataFrame):
    predictions = []
    for index, row in dataFrame.iterrows():
        predictions.append(lynchHardcodedModel.hardCodedModel(row))
    dataFrame['lynchHardcodedPrediction'] = predictions
    return dataFrame
def addPlumpHardcodedPrediction(dataFrame):
    predictions = []
    for index, row in dataFrame.iterrows():
        predictions.append(model_data.tims_hardcoded_rules(row))
    dataFrame['plumpHardcodedPrediction'] = predictions
    return dataFrame

def aggregateData(dataFrame):
    mid1 = addBayesPrediction(dataFrame)
    mid2 = addPlumpHardcodedPrediction(mid1)
    final = addLynchHardcodedPrediction(mid2)
    return final