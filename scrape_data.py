# A file to scrape the data from the Firestore and save it in Python

from google.cloud import firestore

import pandas as pd


db = firestore.Client('urinaltest')
doc_ref = db.collection(u'test-results')
docs = doc_ref.get()

doc_dicts = []

for doc in docs:
	try:
		# print(u'Document data: {}'.format(doc.to_dict()))
		doc_dicts.append(doc.to_dict())
	except Exception as e:
		print(u'No such document!')

# import pdb
# pdb.set_trace()

data_dict = {'name':[], 'timestamp':[], 'age':[], 'height':[], 'urinals':[], 'index':[]}

for key in data_dict.keys():
	for doc_dict in doc_dicts:
		data_dict[key].append(doc_dict.get(key))

df = pd.DataFrame(data_dict)
new_df = pd.DataFrame(df['urinals'].values.tolist()).add_prefix('urinal').join(df)

# new_df.to_csv(CSV_NAME)
# new_df.to_csv('/Users/timplump/Documents/urinal_test_data/db_121218_1240pm.csv')