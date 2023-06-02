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



num_area = (h // num_notes) if h % num_notes == 0 else (h // num_notes) + 1


client = init_client()
frame_count = 0
frame_skip_rate = args.skip
while(True):
    magnitude = []
    frame_num = []
    start = time.time()

    ret, frame = cap.read()
    if not ret:
        print('video error')
        break

    roi = frame[y:y+h, x:x+args.pad]
    roi_gray = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)
    cv.imshow('ROI', roi)

    accumulated_pixel_color = 0

    frame_count += 1
    if frame_count % frame_skip_rate == 0:
        start = time.time()
        for roi_y_idx in range(h): 
            """
            if i is (h-1):
                cnt = i % num_area
                if((accumulated_pixel_color // cnt) < threshold):
                    accumulated_pixel_color = threshold
                # normalize
                avg_color = accumulated_pixel_color // cnt
                
                
                mag = avg_color
                magnitude.append(mag)
                frame_num.append(frame_count)
                accumulated_pixel_color = 0

            elif (i % num_area) is (num_area - 1):
                # white = 255, black = 0. if whiter than 200, cap it to max_white
                if((accumulated_pixel_color // num_area) < threshold):
                    accumulated_pixel_color = 0
                # normalize
                avg_color = accumulated_pixel_color // num_area
                
                
                mag = avg_color
                magnitude.append(mag)
                frame_num.append(frame_count)
                accumulated_pixel_color = 0
     
            else:
                accumulated_pixel_color += (255 - roi_gray[i][0])
            """
            # Exception: Increase accumulated_pixel_color if it is not the last pixel of the frame
            if (roi_y_idx != h-1) and ((roi_y_idx % num_area) != (num_area-1)):
                accumulated_pixel_color += (255 - roi_gray[roi_y_idx][0])

            # Process accumulated_pixel_color if it is the last pixel of the frame
            if (roi_y_idx == h-1) or ((roi_y_idx % num_area) == (num_area-1)):
                cnt = (roi_y_idx % num_area) if (roi_y_idx == h-1) else num_area

                if (accumulated_pixel_color // cnt) < args.threshold:
                    accumulated_pixel_color = cnt * args.threshold

                avg_color = accumulated_pixel_color // cnt
                magnitude.append(avg_color)
                frame_num.append(frame_count)
                accumulated_pixel_color = 0

        df = pd.DataFrame({'magnitude': magnitude, 'frame_num': frame_num})
        n_midi = len(df)
        frame_nums, magnitudes, indexes = df['frame_num'].values, df['magnitude'].values, df.index.values

        # times_myrs = max(frame_nums) - frame_nums  #measure time from oldest crater (first impact) in data
        times_myrs = frame_nums

        myrs_per_beat = 60  #number of Myrs for each beat of music 
        t_data = times_myrs/myrs_per_beat #rescale time from Myrs to beats
        duration_beats = max(t_data)  #duration in beats (actually, onset of last note)
        print('Duration:', duration_beats, 'beats')

        magnitude_normalizer = ValMapper('linear', magnitudes, min(magnitudes), max(magnitudes), 0, 1)
        norm_magnitude = magnitude_normalizer() #normalize data from 0 to 1 
        norm_scale = 1  #lower than 1 to spread out more evenly
        norm_magnitude = norm_magnitude**norm_scale
        pdb.set_trace()

        midi_data = []
        vel_data = []
        velocity_mapper = ValMapper('linear', norm_magnitude[i]**1, 0, 1, args.vel_min, args.vel_max)

        for i in range(n_midi):
            # note_index = round(map_value(y_data[i], 0, 1, 0, num_notes-1))
            note_index = indexes[i] % num_notes
            midi_data.append(note_midis[note_index])

            note_velocity = round(note_vel_mapper()) #bigger craters will be louder
            #we round here because note velocites are integers
            vel_data.append(note_velocity * 1)

        client.send_message("/note", midi_data)
        client.send_message("/velocity", vel_data)
        time.sleep(0.25)
                
        if cv.waitKey(1) & 0xff == ord('q'):
            break


cv.destroyAllWindows()
cv.waitKey(1)

# The following frees up resources and closes all windows
cap.release()
cv.destroyAllWindows()