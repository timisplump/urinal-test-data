
# Load

import pandas as pd
from scipy import stats

MOST_RECENT_FILE = "db_121618_515pm.csv"

GIRL_FILENAME = "dist.female.first.txt"
GUY_FILENAME = "dist.male.first.txt"

def load_genderfile(filename, as_dict=False):
	"""
	If as_dict, return a map from name to 
	"""
	with open(filename, 'r') as f:
		file_contents = f.readlines()

	names = []
	for line in file_contents:
		name = line.strip().split()[0].lower()
		names.append(name)

	if not as_dict:
		return names
	else:
		return {name:index for index, name in enumerate(names)}

def assign_genders(table):
	"""
	Goes through the names in the table and tries to match them 
	to the girl or boy names from the lists.

	Noisy, but a decent way of separating the female and male submissions.
	"""
	girl_names = load_genderfile(GIRL_FILENAME, as_dict=True)
	guy_names = load_genderfile(GUY_FILENAME, as_dict=True)

	max_ind = max(len(girl_names), len(guy_names))

	def map_to_gender(row):
		girl_index = girl_names.get(row['name'].split()[0].lower(), max_ind)
		guy_index = guy_names.get(row['name'].split()[0].lower(), max_ind)
		if girl_index < guy_index:
			return 'F'

		if guy_index < girl_index:
			return 'M'
		return 'UNKNOWN'

	table['gender'] = table.apply(map_to_gender, axis=1)
	return table

def count_empties(table):
	"""
	Goes through the names in the table and counts how many
	empty urinals were in each scenario
	"""
	def count_empties(row):
		empties = 0
		for i in range(7):
			if 'empty' in row['urinal' + str(i)]:
				empties += 1
		return empties

	table['empties'] = table.apply(count_empties, axis=1)
	return table

def analytics(df):
	"""
	Prints some general analytics about the dataset
	"""
	df = count_empties(df)

	guys_table = df[df['gender'] == 'M']
	girls_table = df[df['gender'] == 'F']
	nonbinary_table = df[df['gender'] == 'UNKNOWN']

	print('There are ' + str(len(girls_table)) + ' submissions by girls in the dataset')
	print('There are ' + str(len(guys_table)) + ' submissions by guys in the dataset')
	print('There are ' + str(len(nonbinary_table)) + ' submissions by unknown genders in the dataset')
	print('There are ' + str(len(set(girls_table['name'].values))) + ' separate girl names')
	print('There are ' + str(len(set(guys_table['name'].values))) + ' separate guy names')
	print('There are ' + str(len(set(nonbinary_table['name'].values))) + ' separate unknown gender names')

	# print(set(nonbinary_table['name'].values))

	# To get the modes of the individual scenarios
	grouped_df = df.groupby(['urinal0', 'urinal1', 'urinal2', 'urinal3', 'urinal4', 'urinal5', 'urinal6', 'age', 'gender', 'height'])
	grouped_df = grouped_df.agg({'index': lambda x: tuple(stats.mode(x)[0])[0]})
	print("There are " + str(len(list(grouped_df.iterrows()))) + " separate (urinal, age, gender, height) scenarios")


	print("The average number of empty urinals over the scnarios: " + str(df['empties'].mean()))
	print("The number of scenarios with an empty stall: " + str(len(df[df['urinal6'] == 'stall_empty'])))
	print("The number of scenarios with an occupied stall: " + str(len(df[df['urinal6'] == 'stall_occupied'])))
	print("The number of scenarios with no stall: " + str(len(df[df['urinal6'] == 'none'])))
	
	print("The number of scenarios with an empty kiddie urinal: " + str(len(df[df['urinal0'] == 'kid_empty'])))
	print("The number of scenarios with an occupied kiddie urinal: " + str(len(df[df['urinal0'] == 'kid_occupied'])))
	print("The number of scenarios with no kiddie urinal: " + str(len(df[df['urinal0'] == 'none'])))



df = pd.read_csv(MOST_RECENT_FILE)

df = assign_genders(df)
print(df.head())
analytics(df)

def min_number_of_neighbors(empty_indices, occupied_indices):
	"""
	Returns a tuple: (minimizing_indices, number_of_neighbors)
	which refers to the location(s) with the least number of people
	next to them at the stalls
	"""
	least_num_neighbors = 2
	for index in empty_indices:
		number_of_neighbors = 0
		if index+1 in occupied_indices:
			number_of_neighbors += 1
		if index-1 in occupied_indices:
			number_of_neighbors += 1

		least_num_neighbors = min(number_of_neighbors, least_num_neighbors)

	minimizing_indices = []

	for index in empty_indices:
		number_of_neighbors = 0
		if index+1 in occupied_indices:
			number_of_neighbors += 1
		if index-1 in occupied_indices:
			number_of_neighbors += 1

		if number_of_neighbors == least_num_neighbors:
			minimizing_indices.append(index)

	return (minimizing_indices, least_num_neighbors)

def tims_hardcoded_rules(row):
	"""
	Takes as input a row of the df and outputs which urinal Tim would
	select based on a hardcoded model

	My rules are (higher numbers break ties in lower numbers):
		1. Minimize number of people you are next to
		2. Take regular urinal if possible (over kiddie or stall)
		3. Take kiddie over stall
		4. Leftmost urinal

	Returns an index
	"""

	urinals = [row['urinal' + str(i)] for i in range(7)]
	empty_indices = []
	occupied_indices = []
	for i, urinal in enumerate(urinals):
		if 'empty' in urinal:
			empty_indices.append(i)
		if 'occupied' in urinal:
			occupied_indices.append(i)

	# Rule 1: Get the set of urinals/stalls with the least number of neighbors
	minimizing_indices, _ = min_number_of_neighbors(empty_indices, occupied_indices)

	if len(minimizing_indices) == 1:
		return minimizing_indices[0]
	
	# Rule 2: See how many minimizing_indices are in the regular urinals

	regular_urinal_indices = [index for index in minimizing_indices if 0 < index < 6]
	
	if len(regular_urinal_indices) == 1:
		return regular_urinal_indices[0]
	if len(regular_urinal_indices) > 1: # Jump to Rule 4 if this is the case
		return min(regular_urinal_indices)

	# Rule 3: In this scenario, take the kiddie urinal over the stall
	if 0 in minimizing_indices:
		return 0

	if 6 in minimizing_indices: return 6

	raise NotImplementedError("Hopefully this never happens, but if so, consider this debugging")