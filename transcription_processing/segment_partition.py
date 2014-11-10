from pydub import AudioSegment
import os


def partition_track(track_file):
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


