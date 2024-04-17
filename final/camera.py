import cv2
import numpy as np 

class Camera:

    def __init__(self) -> None:
        self.flowers = []
        self.max_history = 100
        self.cap = cv2.VideoCapture(0)

        ret,self.frame = self.cap.read()
        if not ret:
            raise "Failed to capture frame"

    def calculate_distance(self, point1, point2):
        return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

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
                        self.flowers.append((x,y,radius))
                        #print(x,y,radius)
        return frame
    
    def draw_line(self, img, point1, point2, color=(0, 0, 0), thickness=2):
        cv2.line(img, tuple(map(int, point1)), tuple(map(int, point2)), color, thickness)

    def show_frame(self):
        try:
            cv2.imshow('Object Tracking', self.frame)
        except:
            print("no frame is set")

    def track_flowers(self):
        self.frame = self.process_frame(self.frame)

        for flower in self.flowers:
            center, radius = (flower[0], flower[1]), flower[2]

            # Check if a similar flower is already in the list
            found_similar = False
            for existing_flower in self.flowers:
                if self.calculate_distance(center, existing_flower[0][-1]) < 30:  # Adjust the threshold as needed
                    # Draw lines between the centers of similar flowers in the history
                    for i in range(1, len(existing_flower[0])):
                        self.draw_line(self.frame, existing_flower[0][i - 1], existing_flower[0][i])
                    # Add the current center to the history
                    existing_flower[0].append(center)
                    found_similar = True
                    break

            # If no similar flower is found, add the current flower to the list
            if not found_similar:
                # Initialize the history with the current center
                history = [center]
                self.flowers.append((history, radius))

        # Trim the history to the maximum length
        for i, (history, _) in enumerate(self.flowers):
            self.flowers[i] = (history[-self.max_history:], radius)

        self.show_frame()

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

        
cam = Camera()
while True:
    cam.track_flowers()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cam.release()