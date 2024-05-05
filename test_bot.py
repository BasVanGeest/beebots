import control_bot_keyboard as kb
import camera_copy as cam

def functie():
    kb.listen()
    while True:
        cam.filmthings()

if __name__ == '__main__':
    functie()