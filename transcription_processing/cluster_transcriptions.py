import os
import sys
import pickle
import requests
import feedparser
import numpy as np
import pandas as pd
from time import mktime
from pprint import pprint
from datetime import datetime
from collections import defaultdict
from dateutil.parser import parse
from datetime import datetime, timedelta
import pymongo
from pymongo import MongoClient
from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics.pairwise import pairwise_distances_argmin_min
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.feature_extraction.text import TfidfVectorizer


conn = pymongo.Connection(host='162.243.83.70', port=27017)
db = conn.radioscribe
db.transcribed_segments

station = sys.argv[1]
time = sys.argv[2]
try:
    time = int(sys.argv[2])
except:
    pass

class ClusterStationTranscription(object):
    def __init__(self, station=None, time=None):
        self.station = station
        self.time = time

    
    def start_process(self):
        minute_text_dict = defaultdict(list)
        if time == 'day':
            for i, x in enumerate(db.transcribed_segments.find({"text": {"$ne": ""},"topic": {"$ne":"commercial"},"station":station})):
                try:
                    minute_text_dict[x['id_segment']].append(x['text'])
                except IOError:
                    clean_text = ""
            self.combine_partition_text(minute_text_dict)
        else:
            date = datetime.today() - timedelta(hours = time)
            for i, x in enumerate(db.transcribed_segments.find({"text": {"$ne": ""},"topic": {"$ne":"commercial"}, "time": {"$gte": date}, "station":station})):
                try:
                    minute_text_dict[x['id_segment']].append(x['text'])
                except IOError:
                    clean_text = ""
            self.combine_partition_text(minute_text_dict)
    
    def combine_partition_text(self, minute_text_dict):
        minute_texts = []
        for m in minute_text_dict.items():
            minute_text = ' '.join(m[1])
            minute_texts.append(minute_text)
        self.vectorize_text(minute_texts)

    def vectorize_text(self, minute_texts):
        vectorizer = TfidfVectorizer(ngram_range=(1,4), max_features=20000, stop_words='english')
        X = vectorizer.fit_transform(minute_texts)
        k = 15
        k_means_model, clusters, cluster_contents = self.kmeans_cluster_text(minute_texts, k, X)
        self.create_csv(k, clusters, minute_texts)


    def kmeans_cluster_text(self, minute_texts, k=8, X=None):
        k_means_model = KMeans(n_clusters=k)
        clusters = k_means_model.fit_predict(X)
        
        cluster_contents = defaultdict(list)        
        for i in range(0, len(minute_texts)):
            cluster_contents[clusters[i]].append(minute_texts[i])           
        return k_means_model, clusters, cluster_contents

    
    def create_csv(self, k, clusters, minute_texts):
        cluster_strings = []
        cluster_sizes = {}
        for i in range(0, k):
            sentence_array = np.array(minute_texts)[clusters==i]
            cluster_sizes[i] = sentence_array.shape[0]
            cluster_string = ' '.join(sentence_array)
            cluster_strings.append(cluster_string)
            
        cluster_vectorizer = TfidfVectorizer(stop_words = 'english', ngram_range=(1,3), max_df=0.9)
        cluster_X = cluster_vectorizer.fit_transform(cluster_strings)
        data_file = station + '_' + str(time) +'.csv'
        data_file = '/home/essorensen/radioscribe/app/static/viz_data/' + data_file
        try:
            os.remove(data_file)
        except:
            pass
        for i in range(0, k):
            compressed_indices_of_top_10_words = cluster_X[i,].data.argsort()[-10:]
            full_indices_of_top_10_words = cluster_X[i,].indices[compressed_indices_of_top_10_words]

            cluster_words = cluster_vectorizer.get_feature_names()
            important_word_tuples = []
            for important_word_id in reversed(full_indices_of_top_10_words):
                word = cluster_words[important_word_id]
                tfidf = cluster_X[i, important_word_id]
                with open(data_file, "a") as myfile:
                    string = str(i) +',' + '%30s, %g,' % (word, tfidf) + '%i' % (cluster_sizes[i]) + '\n'
                    myfile.write(string)



run_cluster_job = ClusterStationTranscription(station, time)
run_cluster_job.start_process()
