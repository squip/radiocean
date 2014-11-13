''' entry point for complete process to record, segment, and transcribe live radio stream. '''

import timeshift
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
from pydub import AudioSegment
import speech_recognition as sr
from dateutil import parser
import pymongo
from pymongo import MongoClient

conn = pymongo.Connection()
db = conn.radioscribe
db.transcribed_segments

station = sys.argv[1]

class TranscribeStream(object):
    def __init__(self, station):
        self.station = station

    def start_process(self):
        fileparts = timeshift.main(station, '/usr/local/bin/timeshift.conf')
        file = fileparts[1]
        filenames = self.partition_track(file)
        filenames = [os.path.basename(f) for f in filenames]
        filenames = sorted(filenames)
        pool = ThreadPool(15)
        results = pool.map(self.transcriber, filenames)
        pool.close()
        pool.join()
        # check and make sure none of the workers failed
        for result in results:
            if type(result) == Exception:
                raise result
        for segment, text, part in results:
            self.insert_db_records(segment, text, part)
        
    def insert_db_records(self, segment, text, part):
        original_path = '/home/essorensen/radioscribe/app/static/audio_segments/' + station + '-' + str(segment) + '.mp3'
        created_time = time.ctime(os.path.getctime(original_path))
        created_time = parser.parse(created_time)
        segment_transcribe_doc = {}
        segment_transcribe_doc['id_segment'] = segment
        segment_transcribe_doc['id_part'] = part
        segment_transcribe_doc['text'] = text
        segment_transcribe_doc['time'] = created_time
        segment_transcribe_doc['station'] = station
        segment_transcribe_doc['file'] = os.path.basename(original_path)
        db.transcribed_segments.insert(segment_transcribe_doc)
 

    def partition_track(self, track_file):
        '''
        takes 60s .mp3 file created by timeshift, partitions into 15 equal parts, exports to .wav.

        returns partitioned_segment_list - list of all file paths to the .wav files for each track_file passed to function.
        file name convention - {original segment id}_part_{partition_number} 

        partitioned_segment_list gets passed to transcribe.transcriber
        '''
        track_file_name, fileExtension = os.path.splitext(track_file)
        track_file_base = os.path.basename(track_file_name)
        sound = AudioSegment.from_mp3(track_file)
        segments = range(1,16)
        segment_lengths = []
        segment = len(sound) / 15

        for i in range(1,16):
            segment_length = segment * i
            segment_lengths.append(segment_length)
        
        partioned_segment_list = []
        parts = dict(zip(segments,segment_lengths))
        for k, v in parts.iteritems():
            seg = '_part_' + str(k)
            segment_track_name = track_file_base + seg
            segment_track_path = "/home/essorensen/radioscribe/app/static/audio_segment_partitions/" + segment_track_name + ".wav"
            segment_track_name = sound[v - segment:v]
            segment_track_name = segment_track_name.set_channels(1)
            segment_track_name.export(segment_track_path, format="wav")
            partioned_segment_list.append(segment_track_path)
        return partioned_segment_list

    def transcriber(self, f):
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
        try:
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
                transcribed_text = self.segment_transcribe(segment, segment_dict)
                return transcribed_text
        except Exception as transcription_error:
            return transcription_error


    def segment_transcribe(self, segment, segment_dict):
        text = ''
        transcribed_segments = defaultdict(list)
        for part, file_path in segment_dict.iteritems(): 
            r = sr.Recognizer()
            with sr.WavFile(file_path) as source:        
                audio = r.record(source)                                                                             
            try:
                text = (r.recognize(audio))
                transcribed_segments[segment].append(text)
                print part, segment, text
            except LookupError:
    #            text = '...'
                print("Could not understand audio")
            
            return segment, text, part
    

run_transcription_job = TranscribeStream(station)
run_transcription_job.start_process()







