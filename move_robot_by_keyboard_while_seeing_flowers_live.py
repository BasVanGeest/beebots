from adafruit_servokit import ServoKit
import time
import keyboard_move
from scipy.optimize import fsolve
import cv2
import numpy as np
from adafruit_motorkit import MotorKit

def process_frame(frame):
    flowers = []
    # Convert the frame to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for the color yellow
    lower = np.array([14, 99, 60], dtype="uint8")
    upper = np.array([30, 255, 255], dtype="uint8")


    # Create a mask using the inRange function
    mask = cv2.inRange(hsv_frame, lower, upper)

    # Find contours in the binary mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours on the original frame
    cv2.drawContours(frame, contours, -1, (0, 0, 255), 2)

    # Filter contours based on circularity
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        area = cv2.contourArea(contour)

        if area > 200:
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)

                # You may adjust the circularity threshold based on your requirement
                if 0.2 < circularity < 1.0:
                    # Draw a bounding circle around the contour
                    (x, y), radius = cv2.minEnclosingCircle(contour)
                    center = (int(x), int(y))
                    radius = int(radius)
                    cv2.circle(frame, center, radius, (0, 255, 0), 2)
                    flowers.append((x, y, radius))

    # Draw lines for positioning the flower
    half_width = frame.shape[1] // 2
    quarter_height = frame.shape[0] // 4

    # Horizontal line at 1/4 of the height
    cv2.line(frame, (0, quarter_height), (frame.shape[1], quarter_height), (255, 0, 0), 2)

    # Vertical line at the center of the width
    cv2.line(frame, (half_width, 0), (half_width, frame.shape[0]), (255, 0, 0), 2)

    return frame


# Global variables
scissor_arm_lineair_distance = 25#0
scissor_arm_turn_angle = 0 #7
scissor_arm_pivot_angle = 80 #11
slides = -30



# Initialize ServoKit with specified I2C address
kit = ServoKit(channels=16)

for i in range(16):
    #set pulse width range to 500-2500
    kit.servo[i].set_pulse_width_range(500, 2500)  # Adjust pulse range if needed



def init_scissor_arm():
    global scissor_arm_lineair_distance, scissor_arm_turn_angle, scissor_arm_pivot_angle, slides
    scissor_arm_lineair_distance = 25#0
    scissor_arm_turn_angle = 0 #7
    scissor_arm_pivot_angle = 100 #11
    slides = 35
    move_scissor_arm_lineair(distance_absolute=scissor_arm_lineair_distance)
    kit.servo[7].angle = scissor_arm_turn_angle
    kit.servo[8].angle = scissor_arm_pivot_angle
    kit.servo[11].angle = 180-scissor_arm_pivot_angle
    kit.servo[3].angle = 97-slides

    kit.servo[5].angle = 87+slides
    

def move_slides(angle_increment=None, angle_absolute=None):
    global slides
    if angle_increment is not None:
        new_angle = slides + angle_increment
    elif angle_absolute is not None:
        new_angle = angle_absolute
    else:
        return  # Do nothing if neither angle_increment nor angle_absolute is provided
    kit.servo[3].angle = 97-new_angle
    kit.servo[5].angle = 87+new_angle
    #kit.servo[14].angle = new_angle
    #kit.servo[15].angle = new_angle
    slides = new_angle

    
  
def move_scissor_arm_lineair(distance_increment=None, distance_absolute=None):
    global scissor_arm_lineair_distance
    if distance_increment is not None:
        new_distance = scissor_arm_lineair_distance + distance_increment
    elif distance_absolute is not None:
        new_distance = distance_absolute
        
    else:
        return  # Do nothing if neither angle_increment nor angle_absolute is provided
    
    def load_cubic_line(coefficients_file):
        # Load coefficients from file
        coefficients = np.load(coefficients_file)
        
        # Create a polynomial function
        cubic_line = np.poly1d(coefficients)
        
        return cubic_line

    # Load coefficients from file
    loaded_cubic_line = load_cubic_line('cubic_coefficients_scissor.npy')
    def predict_angle(distance, cubic_line):
        return cubic_line(distance)

    new_angle   = predict_angle(new_distance, loaded_cubic_line)
    print('input distance', new_distance,'output angle: ', new_angle)
    #check if it is between 160 and 109
    if new_angle > 160:
        new_angle = 160
    if new_angle < 109:
        new_angle = 109

    kit.servo[9].angle = new_angle
    scissor_arm_lineair_distance = new_distance
    #print('scissor arm distance: ', new_distance, 'scissor arm angle', new_angle)

def move_scissor_arm_turn(angle_increment=None, angle_absolute=None):
    global scissor_arm_turn_angle
    if angle_increment is not None:
        new_angle = scissor_arm_turn_angle + angle_increment
    elif angle_absolute is not None:
        new_angle = angle_absolute
    else:
        return  # Do nothing if neither angle_increment nor angle_absolute is provided

    if new_angle > 180 or new_angle < 0:
        print("angle out of range")
        return

    kit.servo[7].angle = new_angle
    scissor_arm_turn_angle = new_angle
    print(new_angle)

def move_scissor_arm_pivot(angle_increment=None, angle_absolute=None):
    global scissor_arm_pivot_angle
    if angle_increment is not None:
        new_angle = scissor_arm_pivot_angle + angle_increment
    elif angle_absolute is not None:
        new_angle = angle_absolute
    else:
        return  # Do nothing if neither angle_increment nor angle_absolute is provided

    kit.servo[8].angle = new_angle
    #kit.servo[11].angle = 180-new_angle
    scissor_arm_pivot_angle = new_angle

def main(camera=True):
    # Open a connection to the camera (assuming it's the default camera, change the index if necessary)         
    dc = MotorKit()
    if camera == True:
        cap = cv2.VideoCapture(0)
        # Example usage:
        init_scissor_arm()

        # Check if the camera opened successfully
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return

        # Set the video window size
        window_name = 'Live Stream'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1280, 720)

    while True:
  
        if keyboard_move.is_pressed('left'):
            move_scissor_arm_pivot(angle_increment=3)
            print(scissor_arm_pivot_angle)
            time.sleep(0.1)
        elif keyboard_move.is_pressed('right'):
            move_scissor_arm_pivot(angle_increment=-3)
            print(scissor_arm_pivot_angle)
            time.sleep(0.1)
        elif keyboard_move.is_pressed('a'):
            move_scissor_arm_turn(angle_increment=-5)
            print(scissor_arm_turn_angle)
            time.sleep(0.1)
        elif keyboard_move.is_pressed('d'):
            move_scissor_arm_turn(angle_increment=5)
            print(scissor_arm_turn_angle)
            time.sleep(0.1)
        elif keyboard_move.is_pressed('r'):
            move_scissor_arm_lineair(distance_increment=2)
            print(scissor_arm_lineair_distance)
            time.sleep(0.1)
        elif keyboard_move.is_pressed('e'):
            move_scissor_arm_lineair(distance_increment=-2)
            print(scissor_arm_lineair_distance)
            time.sleep(0.1)
        elif keyboard_move.is_pressed('i'):
            init_scissor_arm()
            print(scissor_arm_lineair_distance)
            time.sleep(0.1)
        elif keyboard_move.is_pressed('up'):
            move_slides(angle_increment=3)
            print(slides)
            time.sleep(0.1)
        elif keyboard_move.is_pressed('down'):
            move_slides(angle_increment=-3)
            print(slides)
            time.sleep(0.1)
        elif keyboard_move.is_pressed('p'):
            # You can now control DC motors connected to the Motor HAT
            # For example, to set the speed of motor M1
            dc.motor1.throttle = 1  #positive it going away from the cabinet
            dc.motor3.throttle = 1   #positive is going away fromt the cabinet
        elif keyboard_move.is_pressed('o'):
            dc.motor1.throttle = -1  #positive it going away from the cabinet
            dc.motor3.throttle = -1   #positive is going away fromt the cabinet
        elif keyboard_move.is_pressed('l'):
            dc.motor1.throttle = 0.0
            dc.motor3.throttle = 0.0
        elif keyboard_move.is_pressed('b'):
            kit.servo[0].angle = 180
        elif keyboard_move.is_pressed('n'):
            kit.servo[0].angle = 0



        if camera == True:
            # Read a frame from the camera
            ret, frame = cap.read()

            # Check if the frame was read successfully
            if not ret:
                print("Error: Could not read frame.")
                break
            frame = process_frame(frame)
            # Display the frame

            cv2.imshow(window_name, frame)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if camera == True:
        # Release the camera and close the window
        cap.release()
        cv2.destroyAllWindows()
    
main()

