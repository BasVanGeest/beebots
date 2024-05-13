import time
import keyboard
import numpy as np

from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)
for i in range(16):
    kit.servo[i].set_pulse_width_range(500, 2500) #set pulse width range to 500-2500 # Adjust pulse range if needed


SARM_LINEAIR_DISTANCE = 25 #0
SARM_TURN_ANGLE = 0 #7
SARM_PIVOT_ANGLE = 80 #11


def init_scissor_arm():
    global SARM_LINEAIR_DISTANCE, SARM_TURN_ANGLE, SARM_PIVOT_ANGLE
    SARM_LINEAIR_DISTANCE = 25 #0
    SARM_TURN_ANGLE = 40 #7
    SARM_PIVOT_ANGLE = 80 #11
    move_scissor_arm_lineair(distance_absolute=SARM_LINEAIR_DISTANCE)
    kit.servo[6].angle = SARM_TURN_ANGLE
    kit.servo[8].angle = SARM_PIVOT_ANGLE
    kit.servo[11].angle = SARM_PIVOT_ANGLE 
  
def move_scissor_arm_lineair(distance_increment=None, distance_absolute=None):
    global SARM_LINEAIR_DISTANCE
    if distance_increment:
        new_distance = SARM_LINEAIR_DISTANCE + distance_increment
    elif distance_absolute:
        new_distance = distance_absolute
    else:
        return
    
    if new_distance > 45 or new_distance < 25:
        return False
    
    print(SARM_LINEAIR_DISTANCE)
    
    def load_cubic_line(coefficients_file):
        coefficients = np.load(coefficients_file)
        return np.poly1d(coefficients)
    loaded_cubic_line = load_cubic_line('cubic_coefficients_scissor.npy')
    def predict_angle(distance, cubic_line):
        return cubic_line(distance)

    new_angle   = predict_angle(new_distance, loaded_cubic_line)
    print('input distance', new_distance,'output angle: ', new_angle)

    if new_angle > 160:
        new_angle = 160
    if new_angle < 109:
        new_angle = 109

    kit.servo[9].angle = new_angle
    SARM_LINEAIR_DISTANCE = new_distance
    return True

def move_scissor_arm_turn(angle_increment=None, angle_absolute=None):
    global SARM_TURN_ANGLE
    if angle_increment:
        new_angle = SARM_TURN_ANGLE + angle_increment
    elif angle_absolute:
        new_angle = angle_absolute
    else:
        return

    if new_angle > 180 or new_angle < 0:
        print("angle out of range")
        return

    kit.servo[6].angle = new_angle
    SARM_TURN_ANGLE = new_angle
    print(new_angle)

def move_scissor_arm_pivot(angle_increment=None, angle_absolute=None):
    global SARM_PIVOT_ANGLE
    if angle_increment:
        new_angle = SARM_PIVOT_ANGLE + angle_increment
    elif angle_absolute:
        new_angle = angle_absolute
    else:
        return 

    if new_angle < 0 or new_angle > 180:
        return

    kit.servo[8].angle = new_angle
    kit.servo[11].angle = new_angle
    SARM_PIVOT_ANGLE = new_angle

def main():
    while True:
        if keyboard.is_pressed('left'):
            move_scissor_arm_pivot(angle_increment=3)
        elif keyboard.is_pressed('right'):
            move_scissor_arm_pivot(angle_increment=-3)
        elif keyboard.is_pressed('a'):
            move_scissor_arm_turn(angle_increment=-5)
        elif keyboard.is_pressed('d'):
            move_scissor_arm_turn(angle_increment=5)
        elif keyboard.is_pressed('up'):
            move_scissor_arm_lineair(distance_increment=2)
        elif keyboard.is_pressed('down'):
            move_scissor_arm_lineair(distance_increment=-2)
        elif keyboard.is_pressed('i'):
            init_scissor_arm()    
        time.sleep(0.1)   
if __name__ == '__main__':
    main()

