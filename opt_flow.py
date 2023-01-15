#!/usr/bin/env python

'''
example to show optical flow

USAGE: opt_flow.py [<video_source>]

Keys:
 1 - toggle HSV flow visualization
 2 - toggle glitch

Keys:
    ESC    - exit
'''

# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2 as cv

import video

# import librosa
# import librosa.display
# import matplotlib.pyplot as plt
# import IPython.display as ipd

printFlag  = True

def draw_flow(img, flow, step=16):
    h, w = img.shape[:2]
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1).astype(int)
    fx, fy = flow[y,x].T
    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    vis = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    cv.polylines(vis, lines, 0, (0, 255, 0))
    for (x1, y1), (_x2, _y2) in lines:
        cv.circle(vis, (x1, y1), 1, (0, 255, 0), -1)
    return vis


def draw_hsv(flow):
    h, w = flow.shape[:2]
    fx, fy = flow[:,:,0], flow[:,:,1]
    ang = np.arctan2(fy, fx) + np.pi
    v = np.sqrt(fx*fx+fy*fy)
    hsv = np.zeros((h, w, 3), np.uint8)
    hsv[...,0] = ang*(180/np.pi/2)
    hsv[...,1] = 255
    # hsv[...,2] = np.minimum(v*4, 255)
    hsv[...,2] = cv.normalize(v, None, 0, 255, cv.NORM_MINMAX)
    bgr = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
    return bgr


def warp_flow(img, flow):
    h, w = flow.shape[:2]
    flow = -flow
    flow[:,:,0] += np.arange(w)
    flow[:,:,1] += np.arange(h)[:,np.newaxis]
    res = cv.remap(img, flow, None, cv.INTER_LINEAR)
    return res

def main():
    import sys

    # input: video_path pixel_x pixel_y
    try:
        vid = sys.argv[1]
        pixel_x = int(sys.argv[2])
        pixel_y = int(sys.argv[3])
        show_hsv = sys.argv[4]
        show_glitch = sys.argv[5]
    except IndexError:
        # vid = 0
        pixel_x = None
        pixel_y = None
        show_hsv = False
        show_glitch = False
    
    if len(sys.argv) > 6:
        vid = 0
        pixel_x = None
        pixel_y = None
        show_hsv = False
        show_glitch = False

    # The video feed is read in as a VideoCapture object
    cam = video.create_capture(vid) # cv.VideoCapture()
    if not cam.isOpened():
        print("Camera open failed!")
        sys.exit()
    # 캠의 속성값을 불러온다.
    w = round(cam.get(cv.CAP_PROP_FRAME_WIDTH))
    h = round(cam.get(cv.CAP_PROP_FRAME_HEIGHT))
    fps = cam.get(cv.CAP_PROP_FPS) # 카메라에 따라 값이 정상적, 비정상적

    # fourcc 값 받아오기, *는 문자를 풀어쓰는 방식, *'DIVX' == 'D', 'I', 'V', 'X'
    fourcc = cv.VideoWriter_fourcc(*'DIVX')

    # 1프레임과 다음 프레임 사이의 간격 설정
    delay = round(1000/fps)

    # 웹캠으로 찰영한 영상을 저장하기
    # cv2.VideoWriter 객체 생성, 기존에 받아온 속성값 입력
    flowout = cv.VideoWriter('./recorded/'+ vid.rstrip('.mp4') +'_flow.avi', fourcc, fps, (w, h))
    hsvout = cv.VideoWriter('./recorded/'+ vid.rstrip('.mp4') +'_hsv.avi', fourcc, fps, (w, h))
    # ret = a boolean return value from getting the frame, first_frame = the first frame in the entire video sequence
    _ret, prev = cam.read()
    # Converts frame to grayscale because we only need the luminance channel for detecting edges - less computationally expensive
    prevgray = cv.cvtColor(prev, cv.COLOR_BGR2GRAY)

    show_hsv = (show_hsv == 'True')
    show_glitch = (show_glitch == 'True')
    cur_glitch = prev.copy()
    magnitude_array = np.array([])
    loopcnt = 0

    while True:
        loopcnt += 1
      	# ret = a boolean return value from getting the frame, frame = the current frame being projected in the video
        _ret, frame = cam.read()
		# prints image size
        # print(np.shape(frame))

		# Converts each frame to grayscale - we previously only converted the first frame to grayscale
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

		# Calculates dense optical flow by Farneback method
    	# https://docs.opencv.org/3.0-beta/modules/video/doc/motion_analysis_and_object_tracking.html#calcopticalflowfarneback
        flow = cv.calcOpticalFlowFarneback(prevgray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        prevgray = gray
        
		##### magnitude and angle #####

        # Print cartesian value of magnitude and angle
        magnitudeInCart = flow[..., 0]
        angleInCart = flow[..., 1]
        # if(printFlag):
            # print(magnitudeInCart, angleInCart)

        # Computes the magnitude and angle of the 2D vectors
        magnitude, angle = cv.cartToPolar(flow[..., 0], flow[..., 1], angleInDegrees = True)
        # if(printFlag):
            # print("magnitude: ", magnitude, "angle: ", angle)
            # print("shape: ", np.shape(magnitude), np.shape(angle))
        
        # prints out polarized magnitude and angle of input pixel position
        pixel_magnitude = magnitude[pixel_x, pixel_y]
        pixel_angle = angle[pixel_x, pixel_y]
        if(printFlag):
          print(pixel_magnitude, pixel_angle)
        magnitude_array = np.append(magnitude_array, pixel_magnitude)
        

        # prints out the average of polarized magnitude and angle
        avg_magnitude = np.average(magnitude)
        avg_angle = np.average(angle)
        # if printFlag:
            # print(avg_magnitude, avg_angle)


		##### print #####  
        flowout.write(draw_flow(gray, flow))
        hsvout.write(draw_hsv(flow))
        cv.imshow('flow', draw_flow(gray, flow))
        if show_hsv:
            cv.imshow('flow HSV', draw_hsv(flow))
        if show_glitch:
            cur_glitch = warp_flow(cur_glitch, flow)
            cv.imshow('glitch', cur_glitch)

        ch = cv.waitKey(1)
        if ch == ord('q'):
            break
        if ch == ord('1'):
            show_hsv = not show_hsv
            print('HSV flow visualization is', ['off', 'on'][show_hsv])
        if ch == ord('2'):
            show_glitch = not show_glitch
            if show_glitch:
                cur_glitch = frame.copy()
            print('glitch is', ['off', 'on'][show_glitch])
    
    cam.release()
    flowout.release()
    hsvout.release()
    fs = loopcnt
    freq = magnitude_array
    x1 = np.sin(2*np.pi*freq*np.arange(freq)/fs)
    # ipd.Audio(x1, rate = fs)
    print(magnitude_array)
    print(loopcnt)
    print('Done')


if __name__ == '__main__':
    print(__doc__)
    main()
    cv.destroyAllWindows()