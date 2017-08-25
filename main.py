# use command line to input 2 files: studio songs list and live concert list file
import sys
import os
from tqdm import tqdm
from pydub import AudioSegment
from audiofingerprint.Fingerprinter import Fingerprinter

# temp audio file directory
temp_dir = 'temp_wav/'

def split_concert_to_time_series_files(concert_path):
    temp_directory_name = 'extract_feature/dejavu/'
    if not os.path.exists(temp_directory_name):
        os.makedirs(temp_directory_name)
    print ("importing concert files...")
    song = AudioSegment.from_file(concert_path, concert_path.split('.')[-1])
    dur_song = song.duration_seconds * 1000
    frame_length = 30 * 1000 # each frame is 5 seconds
    part = int(dur_song / frame_length)

    song_name = os.path.basename(concert_path).split()[0]
    directory_name = temp_directory_name + song_name
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    print ("framing...")
    for i in tqdm(range(part)):
        part_song = song[i * frame_length : (i+1) * frame_length]
        part_name = directory_name + '/' + str(i) + '.wav'
        if os.path.isfile(part_name):
            continue
        part_song.export(part_name, 'wav')

    return directory_name

def recognize_each_concert_part(concert_parts_dir, djv):
    print ("recognizing...")
    part_name_list = {}
    for root, dirs, files in os.walk(concert_parts_dir):
        for audioName in tqdm(files):
            audioPath = os.path.join(root, audioName)
            part_NO = os.path.basename(audioPath).split('.')[0]
            part_predict_name = djv.recognize(FileRecognizer, audioPath)
            try:
                part_name_list[str(part_NO)] = part_predict_name['song_name']
            except:
                continue
    return part_name_list

def change_dic_2_list(dic):
    list_dic = []
    num_list = []
    max = 0
    for item in dic:
        num_list.append(int(item))
    num_list.sort()
    print (num_list)
    for i in num_list:
        list_dic.append(dic[str(i)])
    return list_dic

def combine_redundant(name_list):
    final_list = []
    count = -1
    for item in name_list:
        if count == -1:
            final_list.append(item)
            count += 1

        elif not final_list[count] == item:
            final_list.append(item)
            count += 1

    return final_list

def mp3_to_16bit_mono_files(filepath):
    convert_command = "ffmpeg -i " + filepath + " -acodec pcm_s16le -ac 1 -ar 16000 " + filepath + "_16bit_mono.wav"
    os.system(convert_command)

def strip_songs_list(songlist):
    for songname in songlist:
        newlist = []
        if songname[-1] == '\n':
            songname = songname[:-1]
        newlist.append(songname)
    return newlist

def convert_wav_to_16bit_mono(filepath):
    if not os.path.exist(temp_dir):
        os.mkdir(temp_dir)
    filename, file_extention = os.path.splitext(filepath)
    filename = filename.split('/')[-1]
    song = AudioSegment.from_file(filepath, file_extention)
    # setting song to 16 bit
    song = song.set_sample_width(2)

    # stereo to mono
    song = song.set_channels(1)

    # setting frame rate to 16k
    song = song.set_frame_rate(16000)

    final_path = temp_dir + filename + '.wav'
    song.export(final_path, format='wav')
    return final_path

def absolute_path_to_filename(filepath):
    filename, file_extention = os.path.splitext(filepath)
    return filename.split('/')[-1]
def main():
    if len(sys.argv) != 3:
        print ("argument number error!")
        exit(-1)

    # filename_studio_songs_list = sys.argv[1]
    # filename_live_concert_list = sys.argv[2]
    # for testing, we give some hard code

    filename_studio_songs_list = '/Users/tom55wu/Documents/ComputerScience/' \
                                 'ResearchProjects/MIREX/SetList/lists/linkin_park_studio.txt'
    filename_live_concert_list = '/Users/tom55wu/Documents/ComputerScience/' \
                                 'ResearchProjects/MIREX/SetList/lists/linkin_park_live.txt'

    try:
        studio_songs_list = open(filename_studio_songs_list, 'r').read()
    except:
        print("open studio songs list error!")
        exit(-1)
    # live concert list only consists of one concert file
    try:
        live_concert = open(filename_live_concert_list, 'r').read()
    except:
        print("open live concert list error!")
        exit(-1)

    # subtask 2 starts here

    FRAME_WIDTH = 0.1
    OVER_LAP = 0.05

    fp_songs = []

    studio_songs_list = studio_songs_list.split('\n')
    studio_16bit_mono_songs_list = [new_song for new_song in convert_wav_to_16bit_mono(studio_songs_list)]

    # TODO: the length of each song

    for song_filename in studio_16bit_mono_songs_list:
        fp_song = Fingerprinter(filepath=song_filename, framewidth=FRAME_WIDTH, overlap=OVER_LAP)
        fp_song.init_fingerprints()
        fp_songs.append(fp_song)

    studio_songs_name_list = []
    for song_name in studio_songs_list:
        studio_songs_name_list.append(absolute_path_to_filename(song_name))

    fp_live = Fingerprinter(filepath=livename, framewidth=FRAME_WIDTH, overlap=OVER_LAP)
    fp_live.init_fingerprints()
    ostream = open('stdout', 'a')
    for fp_song, song_name in zip(fp_songs, studio_songs_name_list):
        ostream.write(fp_live.find_position(fp_song)) # start time of each song
        ostream.write(' \t ')
        # ostream.write(end time)
        ostream.write('(for input input sond ID:%s)' % song_name) # this is only for test
    ostream.close()