from sklearn.externals import joblib
import numpy
import pickle
import pandas as pd

# from sklearn.feature_extraction.text import CountVectorizer                                                                                                            
# from sklearn.pipeline import Pipeline                                                                                                                                  
# from sklearn.naive_bayes import MultinomialNB                                                                                                                          
# model = Pipeline([                                                                                                                                                     
#  ('vectorizer',  CountVectorizer(min_df=1, ngram_range=(1, 2))),                                                                                            
#  ('classifier',  MultinomialNB()) ])                                                                                                                                      
# data = pd.read_pickle("training_data.pkl")
# model.fit(numpy.asarray(data['text']), numpy.asarray(data['topic']))                                                                                                   
# joblib.dump(model, 'trained_naive_bayes.pkl')

model = joblib.load('trained_naive_bayes.pkl')                                                                                                                           

transcribed_text = ['car accident']
label_prediction = model.predict(transcribed_text)
for label in label_prediction:
    print label
