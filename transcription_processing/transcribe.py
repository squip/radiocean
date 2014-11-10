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
    '''
    - takes wav file name created by segment_partition, parses the file name, 
    - creates dict mapping original segment to paired partition part number and partion file name. 
    - segment_transcribe is called, takes segment_id, segment_dict, returns the segment id and transcribed text for partition file.
    - run_stream_processor.py calls transcriber to run concurrently on all 15 partitions in parallell.  transcribed text for all partitions are stored in a list mapped to segment id.
    
    Arguments                                                                                                                                           
    --------- 
    f: wav file name of specific partition.  file name convention: {station string}-{timestamp}_{part_id}.
    
    Variables                                                                                                                                           
    ---------
    f_part: segment partition number (1 - 15). parsed from f argument.
    f_timestamp: timestamp of original mp3 (f) creation time.  parsed from f argument. 
    segment: same as f_timestamp - renamed in first for loop.
    segment_groups: dict mapping f_timestamp to file path of partition.
    segment_dict: pairs partition part id to file path.
    transcribed_text: the text returned after calling segment_transcribe(segment, segment_dict). 
    '''
    station = 'kcbs'
    indir= '/home/essorensen/radioscribe/app/static/audio_segment_partitions'
    segment_groups = defaultdict(list)
    f_check = f.split('-')
    track_file_name, fileExtension = os.path.splitext(f)
    f_part = track_file_name.split('_')
    f_part = f_part[2]
    f_timestamp = f_check[1].split('_')
    f_timestamp = f_timestamp[0]
    f = indir + '/' + f
    segment_groups[f_timestamp].append(f)

    for k, filename in segment_groups.iteritems():
        parts = []
        segment_paths = []
        segment = k

        for f in filename:
            f_check = f.split('-')
            track_file_name, fileExtension = os.path.splitext(f)
            f_part = track_file_name.split('_')
            f_part = int(f_part[-1])
            segment_paths.append(f)
            parts.append(f_part)
        segment_dict = dict(zip(parts, segment_paths))
        segment_dict = OrderedDict(sorted(segment_dict.items()))
        transcribed_text = segment_transcribe(segment, segment_dict)
        return transcribed_text



def segment_transcribe(segment, segment_dict):
    text = ''
    transcribed_segments = defaultdict(list)
    for key, v in segment_dict.iteritems(): 
        r = sr.Recognizer()
        with sr.WavFile(v) as source:        
            audio = r.record(source)                                                                             
        try:
            text = (r.recognize(audio))
            transcribed_segments[segment].append(text)
            print segment, text
        except LookupError:
#            text = '...'
            print("Could not understand audio")
        
        return segment, text
