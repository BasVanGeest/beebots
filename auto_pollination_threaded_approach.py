import cv2
import time
import multiprocessing
from adafruit_servokit import ServoKit
import time
import final.keyboard_move as keyboard_move
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


class SharedData:
    def __init__(self, initial_value, initial_flower):
        self.value = multiprocessing.Value('i', initial_value)
        self.lock = multiprocessing.Lock()
        self.event = multiprocessing.Event()
        self.flower_queue = multiprocessing.Queue()
        self.flower = multiprocessing.Array('f', initial_flower)
        self.all_flowers = multiprocessing.Manager().list()
        #image size
        self.image_width = multiprocessing.Value('i', 640)
        self.image_height = multiprocessing.Value('i', 480)

def camera_and_track(shared_data, tracking_flag, tracker_flag):
    cap = cv2.VideoCapture(0)
    window_name = 'Live Stream'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)
    
    while tracking_flag.is_set():
        ret, frame = cap.read()
        frame_copy = frame.copy()
        #print(frame.shape[1] // 2)

        if not ret:
            print("Error: Could not read frame.")
            break
        
        # Read the flower position from the queue
        try:
            flower = shared_data.flower_queue.get_nowait()
            shared_data.flower[:] = flower
        except queue.Empty:
            pass

        _, flowers = process_frame(frame)
        
        #print('camera and track got frame')

        shared_data.all_flowers[:] = flowers  # Update the shared list
        if shared_data.flower[:] != [0,0,0]:
            tolerance = 45
            for flower in flowers:
                if calculate_distance(flower[:2], shared_data.flower[:2]) < tolerance:
                    shared_data.flower[:] = flower 
                    break
                else:
                    shared_data.flower[:] = [1,1,1]

            x, y, radius = shared_data.flower[:]
            cv2.circle(frame_copy, (int(x), int(y)), int(radius), (0, 255, 0), 2)
            cv2.imshow(window_name, frame_copy)
            print('frame_copy')
        else:
            cv2.imshow(window_name, frame)
            print('frame')

        if cv2.waitKey(1) == 27:
            break

        if tracker_flag.is_set():
            break  # Exit the loop when tracker_flag is set

    cap.release()
    cv2.destroyAllWindows()
    print('stop tracking thread')

def stop_tracking(tracking_flag):
    tracking_flag.clear()

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




import threading

# ... (other imports and functions)

def pollinate_slides_in_position():
    for i in range(16):
        #set pulse width range to 500-2500
        kit.servo[i].set_pulse_width_range(500, 2500)  # Adjust pulse range if needed

    global scissor_arm_lineair_distance, scissor_arm_turn_angle, scissor_arm_pivot_angle, slides
    initial_value = 0  # If you don't want to track a flower initially
    # or
    initial_flower = [0, 0, 0]  # Default values for a non-existent flower position

    shared_data = SharedData(initial_value=initial_value, initial_flower=initial_flower)
    center = shared_data.image_width.value/2
    
    time.sleep(3)
    move_slides(position_absolute=10)
    time.sleep(3)
    init_scissor_arm()

    # Start the camera and tracking process in a separate thread
    tracking_flag = threading.Event()
    tracking_flag.set()  # Set the tracking flag to start tracking
    tracker_flag = threading.Event()

    camera_thread = threading.Thread(target=camera_and_track, args=(shared_data, tracking_flag, tracker_flag))
    camera_thread.start()
    time.sleep(3)

    for i in range(47*4):
        targets = []
        move_slides(position_increment=0.25)
        print('slides position', slides)
        time.sleep(0.5)

        # get the new flowers
        flowers = shared_data.all_flowers[:]

        if len(flowers) > 0:
            for flower in flowers:
                if flower[1] < 50:
                    print(flower[1])
                    targets.append(flower)

            if len(targets) > 0:
                targets.sort(key=lambda x: abs(x[0]-center))
                for j in range(len(targets)):
                    target_flower_begin = targets[j]
                    target_flower = targets[j]

                    shared_data.flower_queue.put(target_flower)

                    while abs(target_flower[0]-center) > 10 and target_flower != [0,0,0]:
                        if target_flower[0] < center:
                            move_scissor_arm_pivot(angle_increment=0.5)
                        else:
                            move_scissor_arm_pivot(angle_increment=-0.5)
                        time.sleep(0.5)

                        target_flower = shared_data.flower[:]
                        if target_flower == [1,1,1]:
                            print('lost flower!')
                            target_flower = [0,0,0]
                        #shared_data.flower_queue.put(target_flower)
                    if target_flower != [1,1,1]:
                        distance = distance_to_flower(target_flower_begin, target_flower, scissor_arm_pivot_angle, center)
                        print('algined to flower, distance: ', distance)
                        time.sleep(5)
                        move_scissor_arm_lineair(distance_increment=10)
                        time.sleep(5)
                        move_scissor_arm_lineair(distance_increment=-10)
                        time.sleep(5)


    # Stop the camera thread when the main loop is done
    tracking_flag.clear()
    camera_thread.join()

pollinate_slides_in_position()
"""
init_scissor_arm()

                    
    #now give the target to the camera and tracking process
    shared_data.flower_queue.put(target_flower)


    
    


    initial_flower_position = [0.0, 0.0, 0.0]  # Initial flower position [x, y, radius]
    shared_data = SharedData(initial_value=0, initial_flower=initial_flower_position)

    # Start the camera and tracking process simultaneously
    tracking_flag = multiprocessing.Event()
    tracking_flag.set()  # Set the tracking flag to start tracking
    tracker_flag = multiprocessing.Event()

    processes = []

    # Start the camera and tracking process
    camera_and_track_process = multiprocessing.Process(target=camera_and_track, args=(shared_data, tracking_flag, tracker_flag))
    camera_and_track_process.start()
    processes.append(camera_and_track_process)

    # Example: Send a flower position to the tracking process
    new_flower_position = [100.0, 150.0, 30.0]  # Example new flower position [x, y, radius]
    shared_data.flower_queue.put(new_flower_position)

    # Stop tracking after some time (for demonstration purposes)
    time.sleep(5)
    stop_tracking(tracking_flag)

    # Wait for all processes to finish
    for process in processes:
        process.join()


"""