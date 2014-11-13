from sklearn.externals import joblib
import numpy
import pickle
import pandas as pd
import pymongo
from pymongo import MongoClient

conn = pymongo.Connection()
db = conn.radioscribe
db.transcribed_segments

model = joblib.load('trained_naive_bayes.pkl')

# from sklearn.feature_extraction.text import CountVectorizer                                                                                                            
# from sklearn.pipeline import Pipeline                                                                                                                                  
# from sklearn.naive_bayes import MultinomialNB                                                                                                                          
# model = Pipeline([                                                                                                                                                     
#  ('vectorizer',  CountVectorizer(min_df=1, ngram_range=(1, 2))),                                                                                            
#  ('classifier',  MultinomialNB()) ])                                                                                                                                      
# data = pd.read_pickle("training_data.pkl")
# model.fit(numpy.asarray(data['text']), numpy.asarray(data['topic']))                                                                                                   
# joblib.dump(model, 'trained_naive_bayes.pkl')


#transcribed_text = ['CBS News time 138 traffic and weather together every 10 minutes on the 8th']
#label_prediction = model.predict(transcribed_text)
#for label in label_prediction:
#    print label


unlabeled_transcripts = db.transcribed_segments.find({"text": {"$ne": ""}, "label" : { "$exists" : False } } )
for t in unlabeled_transcripts:
    text= t['text']
    id = t['_id']

    label_prediction = model.predict([text])
    label = label_prediction[0]
    db.transcribed_segments.update({"_id": id}, {"$set": {"label": label}})
    print id, label, text

