import cv2
import time
import multiprocessing
from adafruit_servokit import ServoKit
import time
import keyboard_move
import cv2
import numpy as np 
from scipy.optimize import fsolve
import queue
import cv2
import time
import multiprocessing
import math

scissor_arm_lineair_distance = 25
scissor_arm_turn_angle = 0
scissor_arm_pivot_angle = 97
slides = 5
# Initialize ServoKit with specified I2C address
kit = ServoKit(channels=16)

for i in range(16):
    #set pulse width range to 500-2500
    kit.servo[i].set_pulse_width_range(500, 2500)  # Adjust pulse range if needed


def calculate_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


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

    return frame, flowers

def init_scissor_arm():
    global scissor_arm_lineair_distance, scissor_arm_turn_angle, scissor_arm_pivot_angle, slides
    scissor_arm_lineair_distance = 25#9
    scissor_arm_turn_angle = 0 #7
    scissor_arm_pivot_angle = 97 #11
    #slides = 5
    #move_slides(position_absolute=slides)
    kit.servo[9].angle = scissor_arm_lineair_distance
    move_scissor_arm_lineair(distance_absolute=scissor_arm_lineair_distance)
    kit.servo[7].angle = scissor_arm_turn_angle
    #kit.servo[10].angle = scissor_arm_pivot_angle
    kit.servo[11].angle = 180-scissor_arm_pivot_angle
    

def move_slides(position_increment=None, position_absolute=None):
    global slides
    if position_increment is not None:
        new_position = slides + position_increment
    elif position_absolute is not None:
        new_position = position_absolute
    
    slides = new_position
    

    # Define the inverse function to get angle from distance
    def inverse_cubic_line(distance):
        a=-0.00018213789214182295
        b= 0.0017375297279088456
        c= 0.868231418740067
        d= 21.047484598982045
        # Define the equation: a*x^3 + b*x^2 + c*x + d - distance = 0
        equation = lambda x: a * x**3 + b * x**2 + c * x + d - distance
        # Use fsolve to find the root of the equation (corresponding angle)
        angle = fsolve(equation, 0)[0]
        return angle

    angle = inverse_cubic_line(new_position)

    #check for max and min position
    if angle > 47: 
        ngle = 47
    elif angle < -32:
        angle = -32
 
    kit.servo[3].angle = 97-angle

    kit.servo[5].angle = 87+angle
    slides = new_position

  
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
    
    kit.servo[7] = new_angle

def move_scissor_arm_pivot(angle_increment=None, angle_absolute=None):
    global scissor_arm_pivot_angle
    if angle_increment is not None:
        new_angle = scissor_arm_pivot_angle + angle_increment
    elif angle_absolute is not None:
        new_angle = angle_absolute
    else:
        return  # Do nothing if neither angle_increment nor angle_absolute is provided
    print('pivot angle; ',180 -new_angle)
    #kit.servo[8].angle = new_angle
    kit.servo[11].angle = 180-new_angle
    scissor_arm_pivot_angle = new_angle
    
def get_image(cap):
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame.")
        return None, None

    processed_frame, flowers = process_frame(frame)

    return frame, processed_frame, flowers



def distance_to_flower(target_flower_begin, target_flower_end, scissor_arm_pivot_angle, image_width):
    #calculate the difference in the 2 flower positions
    x1, y1, radius1 = target_flower_begin
    x2, y2, radius2 = target_flower_end

    #the beginning of the scissor arm was at 97 degrees, now it is at scissor_arm_pivot_angle
    #calculate the angle of the scissor arm
    beta = abs(97-scissor_arm_pivot_angle)

    #now let's calculate alpha
    def calculate_alpha(x1, x2, image_width):
        #midline = (1/2 * image_width)/tan(42.5)
        midline = (1/2 * image_width) / math.tan(math.radians(42.5))
        tan_a = (x1 - x2)/midline
        alpha = math.degrees(math.atan(tan_a))

        return alpha
    
    alpha = calculate_alpha(x1, x2, image_width)
    beta = scissor_arm_pivot_angle


    #we use a c270 camera, the field of view is 55 degrees diagonally
    #calculate the angle of the camera
    # Example usage:
    d = 26.5

    def calculate_L(d, alpha, beta):
        alpha_rad = np.radians(alpha)
        beta_rad = np.radians(beta)
        L = d / np.sin(alpha_rad - beta_rad) * np.sin(np.radians(180 - alpha)) - d
        return L
    
    result = calculate_L(d, alpha, beta)
    print("Result:", result)
    return result

def pollinate_slides_in_position():
    for i in range(16):
        #set pulse width range to 500-2500
        kit.servo[i].set_pulse_width_range(500, 2500)  # Adjust pulse range if needed

    global scissor_arm_lineair_distance, scissor_arm_turn_angle, scissor_arm_pivot_angle, slides
    initial_value = 0  # If you don't want to track a flower initially
    time.sleep(3)
    move_slides(position_absolute=10)
    time.sleep(3)
    init_scissor_arm()
    time.sleep(3)

    for i in range(47*4):
        targets = []
        move_slides(position_increment=0.25)
        print('slides position', slides)
        time.sleep(0.5)

        cap = cv2.VideoCapture(0)
        # Check if the webcam is opened correctly
        if not cap.isOpened():
            raise IOError("Cannot open webcam")
        

        # get the new flowers
        frame, processed_frame, flowers= get_image(cap)

        # Release the video capture object
        cap.release()

        center = frame.shape[1] // 2



        if len(flowers) > 0:
            for flower in flowers:
                if flower[1] < 50:
                    targets.append(flower)

            if len(targets) > 0:
                targets.sort(key=lambda x: abs(x[0]-center))
                for j in range(len(targets)):
                    target_flower_begin = targets[j]
                    target_flower = targets[j]

                    init_scissor_arm()
                    time.sleep(1)
                    while abs(target_flower[0]-center) > 10:
                        if target_flower[0] < center:
                            move_scissor_arm_pivot(angle_increment=0.5)
                        else:
                            move_scissor_arm_pivot(angle_increment=-0.5)
                        time.sleep(0.5)
                        cap = cv2.VideoCapture(0)
                        # Check if the webcam is opened correctly
                        if not cap.isOpened():
                            raise IOError("Cannot open webcam")
                        # get the new flowers
                        frame, processed_frame, flowers= get_image(cap)
                        # Release the video capture object
                        cap.release()
                        #let's see which flower is the closest to the target_flower and make that the new target_flower
                        if len(flowers) > 0:
                            for flower in flowers:
                                if flower[1] < 50:
                                    tolerance = 25
                                    if flower[0] > target_flower[0] - tolerance and flower[0] < target_flower[0] + tolerance:
                                        target_flower = flower
                        else:
                            print('no track flower found')
                            break

                         
                        distance = distance_to_flower(target_flower_begin, target_flower, scissor_arm_pivot_angle, center)
                        print('algined to flower, distance: ', distance)
                        time.sleep(5)
                        move_scissor_arm_lineair(distance_increment=distance)
                        time.sleep(5)
                        move_scissor_arm_lineair(distance_absolute=10)
                        time.sleep(3)



pollinate_slides_in_position()