from Fingerprinter import Fingerprinter
import sys
songname = sys.argv[1]

FRAME_WIDTH = 0.1
OVER_LAP =0.05
test1 = Fingerprinter(filepath=songname, framewidth=FRAME_WIDTH, overlap=OVER_LAP)
test1.init_fingerprints()
test2 = Fingerprinter(filepath="data/setList_16bit_mono.wav", framewidth=FRAME_WIDTH, overlap=OVER_LAP)
test2.init_fingerprints()
# test2.print_info()
# print test2.block_distance(test2.fingerprints_binary,test1.fingerprints_binary)
print test2.find_position(test1)

print "Calculated fingerprints now finding"
