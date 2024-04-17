import numpy as np
import matplotlib.pyplot as plt

def fit_cubic_line(data_points):
    angles, distances = data_points[:, 0], data_points[:, 1]
    
    # Fit a cubic polynomial
    coefficients = np.polyfit(distances, angles, 3)
    
    # Save coefficients to a file
    np.save('cubic_coefficients.npy', coefficients)
    
    # Create a polynomial function
    cubic_line = np.poly1d(coefficients)
    
    return cubic_line

def predict_angle(distance, cubic_line):
    return cubic_line(distance)

# Given data points
data_point = np.array([[160, 25], [157, 25], [154, 26], [151, 28], [148, 29.75], [145, 30.9], [142, 32.5], [139, 34],
                       [136, 35], [133, 36.5], [130, 37.75], [127, 39.25], [124, 39.6], [124, 41], [121, 41.5],
                       [118, 42.5], [115, 43], [112, 44], [109, 44.5]])

# Fit a cubic line
cubic_line = fit_cubic_line(data_point)

# Load coefficients from file (just for verification)
saved_coefficients = np.load('cubic_coefficients.npy')
print("Saved Coefficients:", saved_coefficients)

# Predict angle for a given distance
distance_to_predict = 38.5
predicted_angle = predict_angle(distance_to_predict, cubic_line)

# Print the result
print(f"For a distance of {distance_to_predict} units, the predicted angle is {predicted_angle:.2f} degrees.")

# Plotting the original points and the fitted cubic line
plt.scatter(data_point[:, 1], data_point[:, 0], label='Data Points')
x_values = np.linspace(min(data_point[:, 1]), max(data_point[:, 1]), 100)
y_values = cubic_line(x_values)
plt.plot(x_values, y_values, color='red', label='Cubic Line')
plt.xlabel('Distance')
plt.ylabel('Angle')
plt.title('Cubic Line Fit')
plt.legend()
plt.show()
plt.savefig('cubic_fit_scissor_arm__new.png')
