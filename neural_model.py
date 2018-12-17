from model_data import *
from basicAnalysis import *

import pandas as pd

import numpy as np
from keras import models
from keras import layers
from keras import optimizers
from scipy import stats
from keras.callbacks import Callback
import matplotlib.pyplot as plt

def to_one_hot(urinal):
	"""
	Maps the urinal text to a one hot encoding of it
	"""
	one_hot_map = {"none":0, "empty":1, "occupied":2, "kid_empty":3, "kid_occupied":4, "stall_empty":5, "stall_occupied":6}

	one_hot = np.zeros(7)
	one_hot[one_hot_map[urinal]] = 1

	return one_hot

def vectorize(row):
	"""
	Converts a pandas row from the CSV to a tuple of numpy vectors 
	(data, label) for training over. 
	
	The tuple will be: (input, label, empties)

	input:
		An encoding of the stalls:
			For each of the 7 stalls, a one-hot encoding of the stall value -- 7x one-hot (49 total inputs)
		An encoding of gender: 'M', 'F' or 'UNK'							-- One-hot (3 total inputs)
		Age: Float 															-- (1 total input)
		Height: Float 														-- (1 total input)

	label:
		A one-hot encoding of the place the user chose

	empties:
		A list of booleans that are True if the corresponding urinal is empty
	"""

	input_vec = np.zeros(49+3+1+1)
	urinals = [row['urinal' + str(i)] for i in range(7)]

	for index, urinal in enumerate(urinals):
		input_vec[index * 7: index*7 + 7] = to_one_hot(urinal)

	if row['gender'] == 'M':
		input_vec[49] = 1
	if row['gender'] == 'F':
		input_vec[50] = 1
	if row['gender'] == 'UNK':
		input_vec[51] = 1

	input_vec[52] = row['age']
	input_vec[53] = row['height']

	### OUTPUT
	output_vec = np.zeros(7)
	output_vec[int(row['index'])] = 1

	### EMPTIES
	empty_vec = np.zeros(7)
	for index, urinal in enumerate(urinals):
		if "empty" in urinal:
			empty_vec[index] = 1		

	return input_vec, empty_vec, output_vec

def build_model(input_size, output_size=7):
	"""
	Builds a neural network model to handle the data
	"""
	empty_input = layers.Input(shape=(output_size,), name="empty_input")

	input1 = layers.Input(shape=(input_size,), name="main_input")
	x1 = layers.Dense(int(20), activation='tanh')(input1)
	x2 = layers.Dense(int(15), activation='tanh')(x1)
	x3 = layers.Dense(int(15), activation='tanh')(x2)
	out1 = layers.Dense(int(output_size), activation='softmax')(x3)

	out = layers.Multiply(name="output")([out1, empty_input])
	model = models.Model(inputs=[input1, empty_input], outputs=out)

	return model

def make_model(input_size, output_size=7):
	model = build_model(input_size, output_size=output_size)
	model.compile(optimizer=optimizers.Adam(lr=0.001),
			  loss='categorical_crossentropy', #'mse', #
			  metrics=['categorical_accuracy'])

	return model

def get_dataset(train_test_split=(0.8,0.2)):
	df = pd.read_csv(MOST_RECENT_FILE)
	df = assign_genders(df)

	all_data = [[], [], []]

	for index, row in df.iterrows():
		input_vec, empty_vec, output_vec = vectorize(row)
		all_data[0].append(input_vec)
		all_data[1].append(empty_vec)
		all_data[2].append(output_vec)

	test_index_min = int(len(all_data[0]) * train_test_split[0])

	train_data = [np.array(all_data[i][:test_index_min]) for i in range(3)]
	test_data = [np.array(all_data[i][test_index_min:]) for i in range(3)]

	test_rows = range(test_index_min, len(all_data[0]))

	return train_data, test_data, test_rows

def fit_model(model, train_data):
	history = model.fit({"main_input":train_data[0], "empty_input": train_data[1]}, {"output":train_data[2]},
		epochs=2000, batch_size=32, validation_split=0.25)

	return model, history

def predict_test_data(df, model, test_data, test_rows):
	Yhat = model.predict({"main_input":test_data[0], "empty_input": test_data[1]})
	preds = np.argmax(Yhat, axis=1)

	def add_pred_to_row(row):
		if row['Unnamed: 0'] in test_rows:
			return preds[row['Unnamed: 0'] - test_rows[0]]
		else:
			return -1

	df['neural_predictions'] = df.apply(add_pred_to_row, axis=1)
	return df




def get_accuracy(model, dataset):
	Yhat = model.predict({"main_input":dataset[0], "empty_input": dataset[1]})
	accuracy = (np.argmax(Yhat, axis=1) == np.argmax(dataset[2], axis=1)).mean()
	return accuracy

if __name__ == "__main__":
	INPUT_SIZE = 54
	OUTPUT_SIZE = 7


	df = pd.read_csv(MOST_RECENT_FILE)
	df = assign_genders(df)

	train_data, test_data, test_rows = get_dataset()
	model = make_model(input_size=INPUT_SIZE, output_size=OUTPUT_SIZE)
	model, history = fit_model(model, train_data)
	print(list(df.columns.values))

	plt.plot(history.history['categorical_accuracy'])
	plt.plot(history.history['val_categorical_accuracy'])
	plt.title('model accuracy')
	plt.ylabel('accuracy')
	plt.xlabel('Epoch')
	plt.legend(['train', 'validation'], loc='upper left')
	plt.show()

	test_acc = get_accuracy(model, test_data)
	print(test_acc)

	df = predict_test_data(df, model, test_data, test_rows)

	# Write test data to file
	# df.to_csv(MOST_RECENT_FILE)