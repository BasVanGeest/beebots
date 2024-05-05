import cv2
import numpy as np
import random
import control_bot_keyboard as kb
import cProfile

def calculate_distance(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2

def draw_line(img, point1, point2, color=(0, 0, 0), thickness=2):
    cv2.line(img, (int(point1[0]), int(point1[1])), (int(point2[0]), int(point2[1])), color, thickness)

# Each flower is an instance of the Flower class, which stores its measurements and history
class Flower:
    def __init__(self, center, r):
        self.center = center
        self.color = (255 * random.random(), 255 * random.random(), 255 * random.random())
        self.radius = r
        self.history = []
        self.pollinated = False

    def update(self, pos):
        self.history.append(self.center)
        self.center = pos
        if len(self.history) > 25:
            self.history.pop(0)
    
    def histline(self, img):
        for i in range(len(self.history)-1):
            draw_line(img, self.history[i], self.history[i+1], self.color, 1)


class Camera:

    def __init__(self) -> None:
        self.flowers_detected = []
        self.flowers = []
        self.max_history = 100
        self.cap = cv2.VideoCapture(0)

    def process_frame(self, frame):
        
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
                        cv2.circle(frame, center, int(1.5 * radius), (0, 0, 255), 2)
                        self.flowers_detected.append(Flower((x,y), radius))
        return frame
    

    def show_frame(self):
        try:
            cv2.imshow('Object Tracking', self.frame)
        except:
            print("no frame is set")

    def track_flowers(self):
        ret,self.frame = self.cap.read()
        if not ret:
            raise "Failed to capture frame"
        self.frame = self.process_frame(self.frame)

        # For every detected flower in the frame
        x = 0
        for flower in self.flowers_detected:
            for saved_flower in self.flowers:
                distance = calculate_distance(flower.center, saved_flower.center)
                if distance < 1.5 * flower.radius**2:
                    saved_flower.update(flower.center)
                    x = 1
                    break
            if x == 0 and self.flowers_detected:
                self.flowers.append(flower)

        for flower in self.flowers_detected:
            flower.histline(self.frame)
        
        self.show_frame()

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

def filmendan():
    cam = Camera()
    while True:
        cam.track_flowers()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cam.release()
            break

if __name__ == '__main__':
    filmendan()