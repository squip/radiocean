from pydub import AudioSegment
import os

# iterate through all kcbs mp3 files in directory, send to partitioning function.  

# make this the partitioning/ .wav conversion function:
def partition_track(track_file):
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
#    print "partitioned ", len(parts), " new .wav files from ", track_file_base
    return partioned_segment_list


def partition_segment(track_file):
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
        segment_track_name = str(track_file_base) + str('{0:02}'.format(k))
        segment_track_path = "/home/essorensen/radioscribe/app/static/audio_segment_partitions/" + segment_track_name + ".wav"
        segment_track_name = sound[v - segment:v]
        segment_track_name = segment_track_name.set_channels(1)
        segment_track_name.export(segment_track_path, format="wav")
        partioned_segment_list.append(segment_track_path)

    return partioned_segment_list


''' if this script is run by itself, the code below will:
    1) grab all files from /audio_segments directory that have not been partitioned.
    2) partition each file into 15 5-second .wav files.
    3) save files in /audio_segment_partitions directory, labeled by segment id and partition part number.

    for speed, the current proccess for radioscribe does not run this script by itself, so the code below can be ignored. 
    instead, the partition_segment function is imported and then the list of partitions is transcribed concurrently via multithreading process. 
'''


'''
partitioned_file_timestamps = [0]

indir = '/home/essorensen/radioscribe/app/static/audio_segment_partitions/'
for root, dirs, filenames in os.walk(indir):
    for f in filenames:
        f = f.split('-')
        if f[0] == 'kcbs':
            f = f[1].split('_')
            f = int(f[0])
            partitioned_file_timestamps.append(f)
        else:
            continue

        
last_timestamp = max(partitioned_file_timestamps)
indir = '/home/essorensen/radioscribe/static/audio_segments/'
for root, dirs, filenames in os.walk(indir):
    for f in filenames:
        f_timestamp = f.split('-')
        if f_timestamp[0] == 'kcbs':
            f_timestamp = f_timestamp[1].split('_')
            f_timestamp = f_timestamp[0].split('.')
            f_timestamp = int(f_timestamp[0])
            if f_timestamp > last_timestamp:
                f = indir + '/' + f
                try:
                    partition_track(f)
                except:
                    pass
            else:
                continue
        else:
            continue
'''
