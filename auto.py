from camera import Camera
import keyboard_move
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

def move_to(center):
    

cam = Camera()
while True:
    cam.get_frame()
    cam.track_flowers()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cam.release()