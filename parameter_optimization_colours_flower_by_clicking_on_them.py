import cv2
import numpy as np

# Initialize variables for HSV range
highest_h = 0
highest_s = 0
highest_v = 0
lowest_h = 255
lowest_s = 255
lowest_v = 255

# Callback function for mouse event
def on_mouse(event, x, y, flags, param):
    global highest_h, highest_s, highest_v, lowest_h, lowest_s, lowest_v
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = frame[y, x]
        print(f'BGR: {pixel}, HSV: {cv2.cvtColor(np.uint8([[pixel]]), cv2.COLOR_BGR2HSV)}')
        h, s, v = cv2.cvtColor(np.uint8([[pixel]]), cv2.COLOR_BGR2HSV)[0][0]
        if h > highest_h:
            highest_h = h
        if s > highest_s:
            highest_s = s
        if v > highest_v:
            highest_v = v
        if h < lowest_h:
            lowest_h = h
        if s < lowest_s:
            lowest_s = s
        if v < lowest_v:
            lowest_v = v
        print(f'Highest H: {highest_h}, Highest S: {highest_s}, Highest V: {highest_v}')
        print(f'Lowest H: {lowest_h}, Lowest S: {lowest_s}, Lowest V: {lowest_v}')

# Open a video capture object (0 represents the default camera)
cap = cv2.VideoCapture(4)

# Check if the camera is opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Create a window
cv2.namedWindow('image')
cv2.setMouseCallback('image', on_mouse)

while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    # Check if the frame was read successfully
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Show the frame
    cv2.imshow('image', frame)

    # Check for the 'Esc' key to exit
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Release the capture object and close all windows
cap.release()
cv2.destroyAllWindows()
