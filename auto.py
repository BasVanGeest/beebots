from camera import Camera
from keyboard_move import *
import cv2

mid_point = (240,320)


"""
draai camera naar juiste positie
scan bloemen
kies bloem
onthoud start positie  # turn==40, pivot==80, linear==25
ga naar bloem (center bloem in het midden terwijl je dichter bij beweegt)
keer terug naar start positie
"""

# +- 20 so it stays still when within range of middle
def move_to(flower):
    if flower[0] > (mid_point[0] + 40): # down
        move_scissor_arm_pivot(angle_increment=0.5)
        print("down")
    elif flower[0] < (mid_point[0] - 40): # up
        print("up")
        move_scissor_arm_pivot(angle_increment=-0.5)

    # if flower[1] < mid_point[1]: #! left?
    #     print("left")
    #     move_horizontal(angle_increment=-0.5)
    # elif flower[1] > mid_point[1]: #! right? 
    #     print("right")
    #     move_horizontal(angle_increment=0.5)




#TODO: elke bloem lang gaan en bezoeke


def init():
    global mid_point
    init_scissor_arm()
    cam = Camera()
    cam.get_frame()
    cam.track_flowers()
    w,h = cam.frame_size()
    mid_point = (w/2,h/2)
    return cam

out = cv2.VideoWriter('output.avi', -1, 20.0, (640,480))

cam = init()
while True:
    cam.get_frame()
    cam.track_flowers()
    if len(cam.flowers) > 0:
        
        out.write(cam.frame)
        goal = cam.flowers[0].center
        print(goal)
        print(mid_point)
        move_to(goal)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        out.release()
        cam.release()
        break

