import pandas as pd

def hardCodedModel(row):

	"""
	don't want to be next to given a choice
	only go to kiddie urinal when no one is next to you and there are no other possible options without being in between people
	if you have to be next to someone, value ones on the left side more and decrease weights as they go down
	Checkmate is the key when it is available. if  not, then left side is prefereable
	"""
	options = [row[('urinal' + str(i))] for i in range(7)]
	print(options)
	possible = [str(i) for i in range(7) if 'empty' in options[i]]
	print(possible, 'Howdy')

	possible = checkNext(options, possible)

	if len(possible) >= 1:
		print(possible)
		return min(possible)
	else:
		possible = [str(i) for i in range(7) if 'empty' in options[i]]

	if 'empty' in options[6]:
		return 6
	else:
		if len(possible) > 1:
			if min(possible) == 0:
				print('b')
				return possible[1]
			else:
				print('c')
				return min(possible)
		else:
			print('d')
			return possible[0]

	
def checkNext(options, possible):
	newPossible = []
	for urinalIndex in possible:
		print(urinalIndex)
		try:
			if 'occupied' in options[int(urinalIndex) - 1]:
				print(urinalIndex, 'made it')
				continue
		except(IndexError):
			pass
		try:
			if 'occupied' in options[int(urinalIndex) + 1]:
				continue
		except(IndexError):
			pass
		newPossible.append(urinalIndex)
	if len(newPossible) > 1 and min(newPossible) == 0:
		print('here')
		newPossible.remove(0)
	return newPossible


bigData = pd.read_csv('db_121218_1240pm.csv')
for index, row in bigData.iterrows():
	if index < 10:
		print(hardCodedModel(row))
