import pdb
import time
import cv2 as cv
import numpy as np

import argparse
import pandas as pd   #import library for loading data, https://pypi.org/project/pandas/
from midiutil import MIDIFile #import library to make midi file, https://midiutil.readthedocs.io/en/1.2.1/

from utils.audio_utils import select_scale, ValMapper
from utils.osc_utils import init_client


parser = argparse.ArgumentParser(description='')
parser.add_argument('-v', '--video', type=str, default='video.mp4')
parser.add_argument('-r', '--manual_roi', type=str, default='y', help='y/n')
parser.add_argument('--pad', type=int, default=1)
parser.add_argument('-s', '--scale', type=str, default='piano', help='piano, CMajor, etc.')
parser.add_argument('-b', '--tempo', type=int, default=60)
parser.add_argument('-t', '--threshold', type=int, default=0)
parser.add_argument('--skip', type=int, default=1, help='frame skip rate')
parser.add_argument('--mode', type=str, default='linear')
parser.add_argument('-min', '--vel_min', type=int, default=0)
parser.add_argument('-max', '--vel_max', type=int, default=127)
args = parser.parse_args()


note_midis = select_scale(args.scale)
num_notes = len(note_midis)
time_per_beat = round(1 / args.tempo, 6)


cap = cv.VideoCapture(0)
# frame_status = a boolean return value from getting the frame
# first_frame = the first frame in the entire video sequence
frame_status, first_frame = cap.read()
print("Video size in pixel: ", first_frame.shape)

if args.manual_roi == 'y':  # Use manual ROI
    x, y, w, h = cv.selectROI('mouse', first_frame, False)
    print(f"ROI box: {x}, {y}, {w}, {h}")
else: # ?
    x, y, w = first_frame.shape[0] // 2, 50, 0
    h = 88*5 if first_frame.shape[1] < 2000 else 88*10

cv.waitKey(1)
cv.destroyWindow('mouse')
cv.destroyAllWindows()
cv.waitKey(1)

# num_area = (h // num_notes) if (h % num_notes == 0) else (h // num_notes + 1)
n_tgt_area = h // num_notes
n_res_area = h % num_notes

client = init_client()
frame_count = 0
frame_skip_rate = args.skip
pixel_threshold = args.threshold
while(True):
    start = time.time()
    ret, frame = cap.read()
    if not ret:
        print('video error')
        cv.waitKey(1)
        cv.destroyAllWindows()
        cv.waitKey(1)
        break

    roi = frame[y:y+h, x:x+args.pad]
    roi_gray = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)
    cv.imshow('ROI', roi)
    
    frame_count += 1
    # Get pixel value of each row: saved in list(magnitude)
    if frame_count % frame_skip_rate == 0:
        start = time.time()
        start_index = n_res_area // 2
        end_index = h - (n_res_area - start_index)
        assert (end_index - start_index) == (n_tgt_area * num_notes)
        
        data = []
        for roi_y_idx in range(start_index, end_index):
            magnitude = np.mean(roi_gray[roi_y_idx:roi_y_idx+n_tgt_area, :])
            data.append({'frame_num': frame_count, 'magnitude': magnitude})

        df_gray_values = pd.DataFrame(data)
        frame_nums = df_gray_values['frame_num'].values
        magnitudes = df_gray_values['magnitude'].values
        # times_myrs = max(frame_nums) - frame_nums  #measure time from oldest crater (first impact) in data
        times_myrs = frame_nums

        myrs_per_beat = 60  #number of Myrs for each beat of music 
        t_data = times_myrs/myrs_per_beat #rescale time from Myrs to beats
        duration_beats = max(t_data)  #duration in beats (actually, onset of last note)
        print('Duration:', duration_beats, 'beats')

        magnitude2velocity = ValMapper('linear', magnitudes, min(magnitudes), max(magnitudes), args.vel_min, args.vel_max)
        vel_data = magnitude2velocity() #normalize data from 0 to 1 
        midi_data = [note_midis[i % num_notes] for i in range(df_gray_values.shape[0])]
        # pdb.set_trace()
        client.send_message("/note", midi_data)
        client.send_message("/velocity", vel_data)
        time.sleep(0.25)
        end = time.time()
        cost = time_per_beat - (end - start)
        print(cost)
        if cv.waitKey(1) & 0xff == ord('q'):
            break


cv.destroyAllWindows()
cv.waitKey(1)
# The following frees up resources and closes all windows
cap.release()
cv.destroyAllWindows()