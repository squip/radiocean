import timeshift
import segment_partition
import testscribe
import os
import sys
import cPickle as pickle
import multiprocessing
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from collections import defaultdict
from collections import OrderedDict
from datetime import datetime
import time
from time import mktime
from dateutil import parser
import pymongo
from pymongo import MongoClient

conn = pymongo.Connection()
db = conn.radioscribe
db.transcribed_segments

station = sys.argv[1]
fileparts = timeshift.main(station, '/usr/local/bin/timeshift.conf')
file = fileparts[1]
filenames = segment_partition.partition_track(file)
filenames = [os.path.basename(f) for f in filenames]
#indir = '/home/essorensen/radioscribe/app/static/audio_segment_partitions'
output = multiprocessing.Queue()

#for root, dirs, filenames in os.walk(indir):
filenames = sorted(filenames)
pool = ThreadPool(15)
results = pool.map(testscribe.transcriber, filenames)
transcribed_segments = defaultdict(list)
for segment, text in results:
    transcribed_segments[segment].append(text)

for k,v in transcribed_segments.iteritems():
    original_path = '/home/essorensen/radioscribe/app/static/audio_segments/' + station + '-' + str(segment) + '.mp3'
    created_time = time.ctime(os.path.getctime(original_path))
    created_time = parser.parse(created_time)
    text = ' '.join(v)
    segment_transcribe_doc = {}
    segment_transcribe_doc['id_segment'] = k
    segment_transcribe_doc['text'] = text
    segment_transcribe_doc['time'] = created_time
    segment_transcribe_doc['station'] = station
    segment_transcribe_doc['file'] = os.path.basename(file)
    db.transcribed_segments.insert(segment_transcribe_doc)


print original_path
print created_time
print text
pool.close()
pool.join()


