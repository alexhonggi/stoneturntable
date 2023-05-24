import cv2 as cv
import numpy as np
import time

printFlag = False   # for debugging process

# The video feed is read in as a VideoCapture object
# cap = cv.VideoCapture("stoneturntable1.mp4")
cap = cv.VideoCapture(0)  # laptop camera

### image preprocessing ###
w = 480 * 2
h = 480 * 2
y = 1080 // 2 - w // 2
x = 1920 // 2 - h // 2

# ret = a boolean return value from getting the frame, first_frame = the first frame in the entire video sequence
ret, first_frame = cap.read()   # read the very first frame
# Converts frame to grayscale because we only need the luminance channel for detecting edges - less computationally expensive
prev_gray = cv.cvtColor(first_frame, cv.COLOR_BGR2GRAY)
prev_gray = prev_gray[y:y+h, x:x+w]
first_frame = first_frame[y:y+h, x:x+w]
# Creates an image filled with zero intensities with the same dimensions as the frame
mask = np.zeros_like(first_frame)   # frame shape = 1080, 1920, 3
# Sets image saturation to maximum
mask[..., 1] = 255

while(cap.isOpened()):
    start = time.time()
    # ret = a boolean return value from getting the frame, frame = the current frame being projected in the video
    ret, frame = cap.read()
    # Opens a new window and displays the input frame
    # cv.imshow("input", frame)
    # x,y,w,h	= cv.selectROI('img', frame, False)
    if w and h:
        roi = frame[y:y+h, x:x+w]
        cv.imshow('cropped', roi)  # ROI 지정 영역을 새창으로 표시
        cv.moveWindow('cropped', 0, 0) # 새창을 화면 좌측 상단에 이동
        cv.imwrite('./cropped2.jpg', roi)   # ROI 영역만 파일로 저장

    # Converts each frame to grayscale - we previously only converted the first frame to grayscale
    gray = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)
    # Calculates dense optical flow by Farneback method
    # https://docs.opencv.org/3.0-beta/modules/video/doc/motion_analysis_and_object_tracking.html#calcopticalflowfarneback

    flow = cv.calcOpticalFlowFarneback(prev_gray, gray, None, pyr_scale = 0.5, levels = 3, winsize = 5 ,iterations = 3, poly_n = 7, poly_sigma = 1.5, flags = 0)
    # Print cartesian value of magnitude and angle
    magnitudeInCart = flow[..., 0]
    angleInCart = flow[..., 1]
    if(printFlag):
      print(magnitudeInCart, angleInCart)
    # Computes the magnitude and angle of the 2D vectors
    magnitude, angle = cv.cartToPolar(flow[..., 0], flow[..., 1])
    if(printFlag):
      print("magnitude: ", magnitude, "angle: ", angle)
      print("shape: ", np.shape(magnitude), np.shape(angle))
    # Sets image hue according to the optical flow direction
    mask[..., 0] = angle * 180 / np.pi / 2
    # Sets image value according to the optical flow magnitude (normalized)
    mask[..., 2] = cv.normalize(magnitude, None, 0, 255, cv.NORM_MINMAX)
    # Converts HSV to RGB (BGR) color representation
    rgb = cv.cvtColor(mask, cv.COLOR_HSV2BGR)
    # Opens a new window and displays the output frame
    cv.imshow("dense optical flow", rgb)
    # Updates previous frame
    prev_gray = gray
    end = time.time()
    print(end-start)
    # Frames are read by intervals of 1 millisecond. The programs breaks out of the while loop when the user presses the 'q' key
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
# The following frees up resources and closes all windows
cap.release()
cv.destroyAllWindows()