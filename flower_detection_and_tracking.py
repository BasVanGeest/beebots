import cv2
import numpy as np 

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
                    flowers.append((x,y,radius))
                    #print(x,y,radius)
    return frame, flowers



# Function to calculate distance between two points
def calculate_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

# Function to draw a line between two points
def draw_line(img, point1, point2, color=(0, 0, 0), thickness=2):
    cv2.line(img, tuple(map(int, point1)), tuple(map(int, point2)), color, thickness)

# Create a list to store flower information (center and radius)
flowers = []

# Maximum history length
MAX_HISTORY_LENGTH = 100

# Initialize the camera (0 for default camera)
cap = cv2.VideoCapture(0)

# List to store flower information (center, radius, history)
flowers = []

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture frame")
        break

    # Detect flowers in the current frame
    frame, detected_flowers = process_frame(frame)

    for flower in detected_flowers:
        center, radius = (flower[0], flower[1]), flower[2]

        # Check if a similar flower is already in the list
        found_similar = False
        for existing_flower in flowers:
            if calculate_distance(center, existing_flower[0][-1]) < 30:  # Adjust the threshold as needed
                # Draw lines between the centers of similar flowers in the history
                for i in range(1, len(existing_flower[0])):
                    draw_line(frame, existing_flower[0][i - 1], existing_flower[0][i])
                # Add the current center to the history
                existing_flower[0].append(center)
                found_similar = True
                break

        # If no similar flower is found, add the current flower to the list
        if not found_similar:
            # Initialize the history with the current center
            history = [center]
            flowers.append((history, radius))

    # Trim the history to the maximum length
    for i, (history, _) in enumerate(flowers):
        flowers[i] = (history[-MAX_HISTORY_LENGTH:], radius)

    # Display the frame
    cv2.imshow('Object Tracking', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()
