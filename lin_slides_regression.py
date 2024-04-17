import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Data points where each point is [angle, distance]
data_point = np.array([[-31, 2], [-25, 3.9], [-19, 5.8], [-16, 6.9], [-13, 9.2], [-10, 11.8], [-7, 15.2],
                       [-4, 18.4], [-1, 20.9], [2, 23.5], [5, 26.3], [8, 28.8], [11, 31], [14, 33.4],
                       [17, 35.2], [20, 37.5], [23, 39.2], [26, 41.3], [29, 42.8], [32, 44], [38, 46.1],
                       [41, 46.9], [47, 47.7]])

# Extract angles and distances
angles = data_point[:, 0]
distances = data_point[:, 1]

# Define a cubic function
def cubic_line(x, a, b, c, d):
    return a * x**3 + b * x**2 + c * x + d

# Fit the function to the data
params, covariance = curve_fit(cubic_line, angles, distances)

# Generate points for the fitted line
fit_line_angles = np.linspace(min(angles), max(angles), 100)
fit_line_distances = cubic_line(fit_line_angles, *params)

# Plot the original data points and the fitted line
plt.scatter(angles, distances, label='Data Points')
plt.plot(fit_line_angles, fit_line_distances, color='red', label='Fitted Cubic Line')
plt.xlabel('Angle')
plt.ylabel('Distance')
plt.legend()
plt.title('Fitted Cubic Line for Data Points')
plt.show()
plt.savefig('cubic_fit.png')

# Print the coefficients of the fitted cubic line
print(f'Cubic Coefficient: {params[0]:.4f}')
print(f'Quadratic Coefficient: {params[1]:.4f}')
print(f'Linear Coefficient: {params[2]:.4f}')
print(f'Constant Term: {params[3]:.4f}')




import numpy as np
from scipy.optimize import fsolve

# Fitted cubic coefficients
a, b, c, d = params
print(a,b,c,d)


a=-0.00018213789214182295
b= 0.0017375297279088456
c= 0.868231418740067
d= 21.047484598982045
# Define the inverse function to get angle from distance
def inverse_cubic_line(distance):
    # Convert the initial guess to degrees
    initial_guess_deg = 0
    a=-0.00018213789214182295
    b= 0.0017375297279088456
    c= 0.868231418740067
    d= 21.047484598982045
    # Define the equation: a*x^3 + b*x^2 + c*x + d - distance = 0
    equation = lambda x: a * x**3 + b * x**2 + c * x + d - distance
    # Use fsolve to find the root of the equation (corresponding angle)
    angle = fsolve(equation, initial_guess_deg)[0]
    return angle


# Example: Get angle for a specific distance
distance_input = 25.0
angle_output = inverse_cubic_line(distance_input)
print(f'For a distance of {distance_input}, the corresponding angle is: {angle_output:.2f} degrees')
