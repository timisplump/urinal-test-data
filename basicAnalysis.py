import csv

import pandas as pd 


def main():
	bigData = pd.read_csv('db_121218_1240pm.csv')
	ageDf, heightDf = getDistributions(bigData)
	getResponseByUrinalSetup(bigData)

def getDistributions(dataFrame):
	ages = dataFrame.groupby('age')
	heights = dataFrame.groupby('height')
	return ages,heights

def getResponseByUrinalSetup(dataFrame):
	urinals = dataFrame.groupby(['urinal0', 'urinal1', 'urinal2', 'urinal3',	'urinal4', 'urinal5', 'urinal6'])['index']

	print(urinals.describe())
main()