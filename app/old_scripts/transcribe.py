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

conn = pymongo.Connection()
db = conn.transcripts
db.transcript_minutes


def transcriber(start,end,filenames):
    segment_groups = defaultdict(list)
    for f in filenames[start:end]:
        f_check = f.split('-')
        if f_check[0] == 'kcbs':
            track_file_name, fileExtension = os.path.splitext(f)
            f_part = track_file_name.split('_')
            f_part = f_part[2]
            f_timestamp = f_check[1].split('_')
            f_timestamp = f_timestamp[0]
            f = indir + '/' + f
            segment_groups[f_timestamp].append(f)

    for k, filenames in segment_groups.iteritems():
        parts = []
        segment_paths = []
        segment = k
        print k
        for f in filenames:
            f_check = f.split('-')
            track_file_name, fileExtension = os.path.splitext(f)
            f_part = track_file_name.split('_')
            f_part = int(f_part[4])
            segment_paths.append(f)
            parts.append(f_part)
        segment_dict = dict(zip(parts, segment_paths))
        segment_dict = OrderedDict(sorted(segment_dict.items()))
        segment_transcribe(segment, segment_dict)


def segment_transcribe(segment, segment_dict):
    transcribed_segments = defaultdict(list)
    for key, v in segment_dict.iteritems(): 
        r = sr.Recognizer()
        with sr.WavFile(v) as source:        
              # use "test.wav" as the audio source                                                                                                  
            audio = r.record(source)                        # extract audio data from the file                                                      
        try:
            text = (r.recognize(audio))
            transcribed_segments[segment].append(text)
            print text
#            print(text, file='/home/essorensen/radioscribe/app/static/txt/textstream.txt')
        except LookupError:
            text = '...'
            print("Could not understand audio")
    mongo_insert(segment, transcribed_segments)


def mongo_insert(segment, transcribed_segments):
    segment_transcribe_doc_list = []
    for k,v in transcribed_segments.iteritems():
        original_path = '/home/essorensen/radioscribe/app/static/audio_segments/kcbs-' + str(segment) + '.mp3'
        created_time = time.ctime(os.path.getctime(original_path))
        created_time = parser.parse(created_time)
        text = ' '.join(v)
        segment_transcribe_doc = {}
        segment_transcribe_doc['id_semgent'] = k
        segment_transcribe_doc['text'] = text
        segment_transcribe_doc['time'] = created_time
        segment_transcribe_doc_list.append(segment_transcribe_doc)
        db.transcript_minutes.insert(segment_transcribe_doc)
    print segment_transcribe_doc_list


indir = '/home/essorensen/radioscribe/app/static/audio_segment_partitions'
for root, dirs, filenames in os.walk(indir):
    batches = len(filenames)/ 30
    batch_end = [i * 30 for i in range(batches)]
    batch_start = [i - 30 for i in batch_end]

next_batch = zip(batch_start, batch_end)
filenames = sorted(filenames)
for start, end in next_batch[0:]:
    transcriber(start,end,filenames)
