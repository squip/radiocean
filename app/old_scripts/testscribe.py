import speech_recognition as sr
import os 
from collections import defaultdict
from collections import OrderedDict
from datetime import datetime
import time
from time import mktime
from dateutil import parser
import pymongo
from pymongo import MongoClient
import multiprocessing as mp

conn = pymongo.Connection()
db = conn.live_transcription
db.segments


def transcriber(f):
    station = 'kcbs'
    indir= '/home/essorensen/radioscribe/app/static/audio_segment_partitions'
    segment_groups = defaultdict(list)
    f_check = f.split('-')
#    f_check = f_check[0].split('/')
#    if f_check[0] == station:
    track_file_name, fileExtension = os.path.splitext(f)
#        print track_file_name
    f_part = track_file_name.split('_')
    f_part = f_part[2]
    f_timestamp = f_check[1].split('_')
#        print f_timestamp
    f_timestamp = f_timestamp[0]
    f = indir + '/' + f
    segment_groups[f_timestamp].append(f)

    for k, filename in segment_groups.iteritems():
        parts = []
        segment_paths = []
        segment = k
 #       print k
        for f in filename:
 #           print f
            f_check = f.split('-')
            track_file_name, fileExtension = os.path.splitext(f)
  #          print track_file_name
            f_part = track_file_name.split('_')
            f_part = int(f_part[-1])
#             print f_part
            segment_paths.append(f)
            parts.append(f_part)
        segment_dict = dict(zip(parts, segment_paths))
        segment_dict = OrderedDict(sorted(segment_dict.items()))
   #     print segment, segment_dict
#        segment = str(f_timestamp) + str('{0:02}'.format(f_part))
        transcribed_text = segment_transcribe(segment, segment_dict)
        return transcribed_text



def segment_transcribe(segment, segment_dict):
    text = ''
    transcribed_segments = defaultdict(list)
    for key, v in segment_dict.iteritems(): 
        r = sr.Recognizer()
        with sr.WavFile(v) as source:        
              # use "test.wav" as the audio source                                                                                                  
            audio = r.record(source)                        # extract audio data from the file                                                      
        try:
            text = (r.recognize(audio))
            transcribed_segments[segment].append(text)
            print segment, text
        except LookupError:
#            text = '...'
            print("Could not understand audio")
        
        return segment, text
