from sklearn.externals import joblib
import pickle 

model = joblib.load('naive_bayes_model.pkl')
transcribed_text = ['car accident']
model.fit(numpy.asarray(data['text']), numpy.asarray(data['topic']))
label_prediction = pipeline.predict(transcribed_text)
for label in label_prediction:
    print label
