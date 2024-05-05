import time
from pynput import keyboard
import numpy as np

from adafruit_servokit import ServoKit
kit = ServoKit(channels=16)
for i in range(16):
    kit.servo[i].set_pulse_width_range(500, 2500) #set pulse width range to 500-2500 # Adjust pulse range if needed


SARM_LINEAIR_DISTANCE = 25 #0
SARM_TURN_ANGLE = 0 #7
SARM_PIVOT_ANGLE = 80 #11
PLATFORM_DISTANCE = 10


def init_scissor_arm():
    global SARM_LINEAIR_DISTANCE, SARM_TURN_ANGLE, SARM_PIVOT_ANGLE
    SARM_LINEAIR_DISTANCE = 25 #0
    SARM_TURN_ANGLE = 0 #7
    SARM_PIVOT_ANGLE = 80 #11
    move_scissor_arm_lineair(distance_absolute=SARM_LINEAIR_DISTANCE)
    kit.servo[7].angle = SARM_TURN_ANGLE
    kit.servo[8].angle = SARM_PIVOT_ANGLE
    kit.servo[11].angle = SARM_PIVOT_ANGLE 

def init_platform():
    kit.servo[0].angle = 0
    kit.servo[1].angle = 0
    kit.servo[2].angle = 0
    kit.servo[3].angle = 0
    print(kit.servo[0].angle)
    print(kit.servo[1].angle)
    print(kit.servo[2].angle)
    print(kit.servo[3].angle)
  
def move_scissor_arm_lineair(distance_increment=None, distance_absolute=None):
    global SARM_LINEAIR_DISTANCE
    if distance_increment:
        new_distance = SARM_LINEAIR_DISTANCE + distance_increment
    elif distance_absolute:
        new_distance = distance_absolute
    else:
        return
    
    if new_distance > 45 or new_distance < 25:
        return
    
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

    kit.servo[7].angle = new_angle
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

def move_platform(angle_increment=None, angle_absolute=None):
    global PLATFORM_DISTANCE
    #kit.servo[0].angle += angle_increment
    #kit.servo[1].angle += angle_increment
    print('0: ' + str(kit.servo[0].angle))
    print('1: ' + str(kit.servo[1].angle))
    print('2: ' + str(kit.servo[2].angle))
    print('3: ' + str(kit.servo[3].angle))
    


def on_press(key):
    pass

def on_release(key):
    if key == keyboard.Key.esc:
        return False
    if key == keyboard.Key.left:
        move_scissor_arm_pivot(angle_increment=1)
    elif key == keyboard.Key.right:
        move_scissor_arm_pivot(angle_increment=-1)
    
    elif key == keyboard.Key.up:
        move_scissor_arm_lineair(distance_increment=1)
    elif key == keyboard.Key.down:
        move_scissor_arm_lineair(distance_increment=-1)

    else:
        try:
            key.char
            if key.char == 'a':
                move_scissor_arm_turn(angle_increment=-5)
            elif key.char == 'd':
                move_scissor_arm_turn(angle_increment=5)
            if key.char == 'w':
                move_platform(angle_increment=-5)
            elif key.char == 's':
                move_platform(angle_increment=5)
            elif key.char == 'i':
                init_scissor_arm()
                init_platform()
 
        except:
            pass

def listen():
    with keyboard.Listener(
        on_press = on_press,
        on_release = on_release) as listener:
        listener.join()

if __name__ == '__main__':
    listen()