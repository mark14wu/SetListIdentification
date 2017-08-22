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

def main():
    if len(sys.argv) != 3:
        print ("argument number error!")
        exit(-1)

    filename_studio_songs_list = sys.argv[1]
    filename_live_concert_list = sys.argv[2]

    try:
        studio_songs_list = open(filename_studio_songs_list, 'r').readlines()
    except:
        print("open studio songs list error!")
    # live concert list only consists of one concert file
    try:
        live_concert = open(filename_live_concert_list, 'r').readline()
    except:
        print("open live concert list error!")

    # subtask 2 starts here

    songname = sys.argv[1]
    livename = "data/setList_16bit_mono.wav"
    FRAME_WIDTH = 0.1
    OVER_LAP = 0.05

    # for studio_song in tqdm(studio_songs_list):
    #     # add songs into database
    #     if studio_song[-1] == '\n':
    #         studio_song = studio_song[:-1]
    #     try:
    #         djv.fingerprint_file(studio_song, song_number)
    #     except:
    #         continue
    #     song_number += 1

    fpsongs = []

    studio_songs_list = strip_songs_list(studio_songs_list)
    studio_16bmono_songs_list = studio_songs_list

    for song_filename in studio_16bmono_songs_list:
        fpsong = Fingerprinter(filepath=song_filename, framewidth=FRAME_WIDTH, overlap=OVER_LAP)
        fpsong.init_fingerprints()
        fpsongs.append(fpsong)

    fplive = Fingerprinter(filepath=livename, framewidth=FRAME_WIDTH, overlap=OVER_LAP)
    fplive.init_fingerprints()
    # test2.print_info()
    # print test2.block_distance(test2.fingerprints_binary,test1.fingerprints_binary)
    ostream = open('stdout', 'a')
    for fpsong, songname in zip(fpsongs, studio_songs_list):
        ostream.write(fplive.find_position(fpsong))
    ostream.close()