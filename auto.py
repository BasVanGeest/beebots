from camera import Camera
from keyboard_move import *
import cv2

mid_point = (240,320)
# def start_cam():
#     cam = Camera()
#     while True:
#         cam.track_flowers()
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             cam.release()

# start cam
# track_flower to find all flowers in the scene
# move trough flower list
# move to each flower


"""
draai camera naar juiste positie
scan bloemen
kies bloem
onthoud start positie
ga naar bloem (center bloem in het midden terwijl je dichter bij beweegt)
keer terug naar start positie
"""


def move_to(flower):
    if flower[0] < mid_point[0]: # down
        move_scissor_arm_pivot(angle_increment=-3)
    elif flower[0] < mid_point[0]: # up
        move_scissor_arm_pivot(angle_increment=-3)

    if flower[1] < mid_point[1]: #! left?
        move_scissor_arm_turn(angle_increment=-5)
    elif flower[1] < mid_point[1]: #! right? 
        move_scissor_arm_turn(angle_increment=-5)


#TODO: turn camera sideways (kwast moet onder de camera)

#TODO: scan

#TODO: elke bloem lang gaan en bezoeken
#TODO: while loop to move to flower (bezoeken)
"""
while true:
    if flower is not within ... pixels of center:
        move_to(flower center)
    if flower is still visible:    (maybe oustside loop)
        !move closer?              (bloem moet onder de camera zitten)
    else:
        break

"""

cam = Camera()
while True:
    cam.get_frame()
    cam.track_flowers()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cam.release()