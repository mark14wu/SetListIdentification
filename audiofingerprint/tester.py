from tqdm import tqdm
import os

temp_path = "data/"
filepaths = open("data/studio_list.txt").readlines()
for filepath in tqdm(filepaths):
	if filepath[-1] == '\n':
		filepath = filepath[:-1]
	filename = filepath.split('/')[-1]
	filename = filename.split('.')[0]
	# print filename
	wavefilename = temp_path + filename + "_16bit_mono.wav"
	# print convert_command
	print filename
	os.system("python fingerprinter_test2.py " + wavefilename)