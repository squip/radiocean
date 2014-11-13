import pymongo
from pymongo import MongoClient
from sklearn.externals import joblib
import numpy
import pickle
import pandas as pd

conn = pymongo.Connection()
db = conn.radioscribe
db.transcribed_segments

    
model = joblib.load('trained_naive_bayes.pkl')

unlabeled_transcripts = db.transcribed_segments.find({"text": {"$ne": ""}, "label" : { "$exists" : False } } )
for t in unlabeled_transcripts:
    text= t['text']
    id = t['_id']
    
    label_prediction = model.predict([text])
    label = label_prediction[0] 
    db.transcribed_segments.update({"_id": id}, {"$set": {"label": label}})
    print id, label, text

