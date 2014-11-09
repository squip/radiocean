import cPickle as pickle
import os
import pymongo
from pymongo import MongoClient

conn = pymongo.Connection()
db = conn.radioscribe
db.transcribed_segments

document_batch = []

# load all pickled dicts in text_queue dir. 
indir = '/home/essorensen/radioscribe/app/static/text_queue/'
for root, dirs, filenames in os.walk(indir):
    for f in filenames:
        file_path = indir+f
        document = pickle.load( open( file_path, "rb" ) )
        document_batch.append(document)
        os.remove(file_path)

# insert batch of dicts to mongo transcribed_segments collection
db.transcribed_segments.insert(document_batch)
