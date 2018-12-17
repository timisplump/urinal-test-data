import pandas as pd
import lynchHardcodedModel
import bayesianModel
import model_data
import aggregateData

def main():
    bigData = pd.read_csv('db_121618_515pm.csv')
    ageDf, heightDf = getDistributions(bigData)
    individuals = bigData.groupby(['name'])['age']
    #print(ageDf.mean())
    #bayesianModel.bayesianModel(bigData)
    #print(bigData['height'].mean(), 'means')
    #getResponseByUrinalSetup(bigData)
    #data = model_data.assign_genders(bigData)
    newData = aggregateData.aggregateData(bigData)
    getHardcodedAccuracy(newData)
    print(newData.dtypes, 'hello')
    newData = newData[newData['gender'] == 'F']
    predictions = newData.groupby(['urinal6'])['index']
    stall = predictions.get_group('stall_empty')
    s =0
    for value in stall:
        if value == 6:
            s += 1
    print(s/len(stall))
    #print(stall)
    print(predictions.describe())
    
    #inconsistentAnswers(newData)
    #m = data.groupby(['name']).size()
    #print(m.get_group('UNKNOWN'))
    #print(m.describe())
    print('done')
    
def checkForInaccuracies(dataFrame):
    scenarios = dataFrame.groupby(['urinal0', 'urinal1', 'urinal2', 'urinal3', 'urinal4', 'urinal5', 'urinal6'])
    
    
def getHardcodedAccuracy(dataFrame):
    alexData = dataFrame[dataFrame['name']== 'Alex Lynch']
    alex = 0
    plumpData = dataFrame[dataFrame['name'] == 'Tim Plump']
    plump = 0
    for index, row in alexData.iterrows():
        if row['index'] == row['lynchHardcodedPrediction']:
            alex += 1
    for index,row in plumpData.iterrows():
        if row['index'] == row['plumpHardcodedPrediction']:
            plump += 1
    results_1 = alex/len(alexData)
    results_2 = plump/len(plumpData)
    print(results_1, 'alex accuracy')
    print(results_2, 'plump accuracy')
    
def averageAge(dataFrame):
    s = 0
    seen = set()
    for index, row in dataFrame.iterrows():
        if row['name'] in seen:
            continue
        else:
            seen.add(row['name'])
            s += row['age']
    return s/len(seen)

def averageHeight(dataFrame):
    s = 0
    seen = set()
    for index, row in dataFrame.iterrows():
        if row['name'] in seen:
            continue
        else:
            seen.add(row['name'])
            s += row['height']
    return s/len(seen)

def inconsistentAnswers(dataFrame):
    groups = dataFrame.groupby(['urinal0', 'urinal1', 'urinal2', 'urinal3', 'urinal4', 'urinal5', 'urinal6']).groups
    #print(groups)
    inconsistent = {}
    for group in groups.keys():
        consistencyDict = {}
        seen = set()
        for index in groups[group]:
            if dataFrame.iloc[index]['name'] in seen:
                test = dataFrame.iloc[index]['index']
                consistencyDict[dataFrame.iloc[index]['name']][test] = index
            else:
                seen.add(dataFrame.iloc[index]['name'])
                consistencyDict[dataFrame.iloc[index]['name']] = {dataFrame.iloc[index]['index']:index}
        for name in consistencyDict.keys():
            if len(consistencyDict[name].keys()) > 1:
                index = dataFrame.iloc[next(iter(consistencyDict[name]))]
                consistencyDict[name]['name']  = name
                inconsistent[index['urinals']] = consistencyDict[name]
    print(inconsistent)
def getDistributions(dataFrame):
    ages = dataFrame.groupby('age')
    heights = dataFrame.groupby('height')
    return ages,heights

def getResponseByUrinalSetup(dataFrame):
    urinals = dataFrame.groupby(['urinal0', 'urinal1', 'urinal2', 'urinal3', 'urinal4', 'urinal5', 'urinal6'])['index']
    print(urinals.describe())
    
def seperateGuysAndGirls(dataFrame):
    namefile = open('dist.male.first.txt', 'r')
    df = pd.read_table('dist.male.first.txt', delim_whitespace=True, names=('name','number1','number2','number3'))
    boyNames = df['name'].tolist()
    df = pd.read_table('dist.female.first.txt', delim_whitespace=True, names=('name','number1','number2','number3'))
    girlNames = df['name'].tolist()
    boyData = []
    girlData = []
    leftoverData = []
    for index, row in dataFrame.iterrows():
        name = row['name'].split(' ')
        if name[0].upper() in girlNames:
            print(row['name'])
            girlData.append(index)
        elif name[0].upper() in boyNames:
            boyData.append(index)
        else:
            #print(row['name'])
            leftoverData.append(index)
    #print(boyData, 'boyData')
    #print(girlData, 'girlData')
    #print((leftoverData), 'leftover')
def addBayesPrediction(dataFrame):
    model = bayesianModel(dataFrame)
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

