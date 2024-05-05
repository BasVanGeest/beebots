import threading
import time
import cProfile

import control_bot_keyboard as kb
import camera_copy as cam

threading.Thread(target=kb.listen).start()
threading.Thread(target=cam.filmendan).start()

