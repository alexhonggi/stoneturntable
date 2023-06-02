import pdb

import time
import cv2 as cv
import numpy as np

import pandas as pd   #import library for loading data, https://pypi.org/project/pandas/
from midiutil import MIDIFile #import library to make midi file, https://midiutil.readthedocs.io/en/1.2.1/

from utils.scale_utils import select_scale, map_value
from utils.osc_utils import init_client


note_midis = select_scale(3)
num_notes = len(note_midis)
client = init_client()

printFlag = True   # for debugging process
testFlag = True

if(testFlag):
    # video = "lp1.mov"
    video = "test.mp4"
    # cap = cv.VideoCapture(video)
    cap = cv.VideoCapture("./video/" + video)
else:
    video = str(input('Video to use: '))
    if (video == "rt"): 
        video = int(0)

    cap = cv.VideoCapture(video)


### image preprocessing ###
# w = 1
# h = 480 * 2
# y = 1080 // 2 - w // 2
# x = 1920 // 2 - h // 2

# ret = a boolean return value from getting the frame, first_frame = the first frame in the entire video sequence
ret, first_frame = cap.read()   # read the very first frame
print("video size in pixel: ", np.shape(first_frame))
if(testFlag):
    isManual = bool(False)
else:
    isManual = str(input('Select ROI in manual? (y/n):'))
    if (isManual == "y"):
        isManual = bool(True)
    else:
        isManual = bool(False)

if(isManual):
    # if want to select area manually
    x, y, w, h = cv.selectROI('mouse', first_frame, False)
    print("x_pos, y_pos: ", x, y)
    print("width, height: ", w, h)
    cv.waitKey(1)
    cv.destroyWindow('mouse')
    cv.destroyAllWindows()
    cv.waitKey(1)
else:
    x, y, w = np.shape(first_frame)[0] // 2, 50, 0
    if(np.shape(first_frame)[1] < 2000):
        h = 88*5
    else:
        h = 88*10
    # x, y, w, h = 1080, 75, 0, 1000

prev_frame_cnt = 0
frame_cnt = 0
bound = 0
leap = 3
tempo = 60

if h % num_notes == 0:
    num_area = (h // num_notes) 
else:
    num_area = (h // num_notes) + 1


while(True):
    magnitude = []
    age = []
    start = time.time()
    ret, frame = cap.read()
    if not ret:
        print('video error')
        cv.waitKey(1)
        cv.destroyAllWindows()
        cv.waitKey(1)
        break

    frame_cnt += 1
    roi = frame[y:y+h, x:x+1]
    roi_gray = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)

    accumulated_pixel_color = 0
    if frame_cnt % leap == 0:
        start = time.time()
        for i in range(h): 
            if i is (h-1):
                cnt = i % num_area
                if((accumulated_pixel_color // cnt) < bound):
                    accumulated_pixel_color = bound
                # normalize
                avg_color = accumulated_pixel_color // cnt
                mag = avg_color

                magnitude.append(mag)
                age.append(frame_cnt)
                accumulated_pixel_color = 0

            elif (i % num_area) is (num_area - 1):
                # white = 255, black = 0. if whiter than 200, cap it to max_white
                if((accumulated_pixel_color // num_area) < bound):
                    accumulated_pixel_color = 0
                # normalize
                avg_color = accumulated_pixel_color // num_area
                mag = avg_color
                magnitude.append(mag)
                age.append(frame_cnt)
                accumulated_pixel_color = 0
            else:
                accumulated_pixel_color += (255 - roi_gray[i][0])

        dict = {'magnitude': magnitude, 'age': age}
    
        df = pd.DataFrame(dict)

        n_impacts = len(df)
        
        ages = df['age'].values 
        magnitudes = df['magnitude'].values 
        indexes = df.index.values
        # print(indexes)

        # times_myrs = max(ages) - ages  #measure time from oldest crater (first impact) in data
        times_myrs = ages

        myrs_per_beat = 60  #number of Myrs for each beat of music 
        t_data = times_myrs/myrs_per_beat #rescale time from Myrs to beats
        duration_beats = max(t_data)  #duration in beats (actually, onset of last note)
        print('Duration:', duration_beats, 'beats')
            
        norm_magnitude = map_value(magnitudes, min(magnitudes), max(magnitudes), 0, 1) #normalize data, so it runs from 0 to 1 
        norm_scale = 1  #lower than 1 to spread out more evenly
        norm_magnitude = norm_magnitude**norm_scale

        vel_min,vel_max = 0, 127   #minimum and maximum note velocity
        midi_data = []
        vel_data = []

        for i in range(n_impacts):
            # note_index = round(map_value(y_data[i], 0, 1, 0, num_notes-1))
            note_index = indexes[i] % num_notes
            midi_data.append(note_midis[note_index])

            note_velocity = round(map_value(norm_magnitude[i]**1, 0, 1, vel_min, vel_max)) #bigger craters will be louder
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