import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit, root_scalar

# File path
file_path = r"C:\Users\Gus\Documents\prediction data.xlsx"

# Read the data
data = pd.read_excel(file_path)

# Ensure the Timestamp column is in datetime format
data['Timestamp'] = pd.to_datetime(data['Timestamp'])

# Filter the data based on the specific timestamp
filtered_data = data[data['Timestamp'].dt.time > pd.to_datetime('17:27:40').time()]

# Extract the pressure and time data
pressure = filtered_data["[edge]STS2/Sensor/PT710"].values
time = filtered_data["Timestamp"].values

# Convert time to numeric values (seconds or minutes from the first time point)
time_numeric = (time - time[0]).astype('timedelta64[s]').astype(float)

# Define the polynomial functions
def linear(x, a, b):
    return a * x + b

def quadratic(x, a, b, c):
    return a * x**2 + b * x + c

def cubic(x, a, b, c, d):
    return a * x**3 + b * x**2 + c * x + d

def quartic(x, a, b, c, d, e):
    return a * x**4 + b * x**3 + c * x**2 + d * x + e

# Fit the data to each polynomial
popt_linear, _ = curve_fit(linear, time_numeric, pressure)
popt_quadratic, _ = curve_fit(quadratic, time_numeric, pressure)
popt_cubic, _ = curve_fit(cubic, time_numeric, pressure)
popt_quartic, _ = curve_fit(quartic, time_numeric, pressure)

# Generate data for plotting the fits
time_fit = np.linspace(min(time_numeric), max(time_numeric), 100)
pressure_fit_linear = linear(time_fit, *popt_linear)
pressure_fit_quadratic = quadratic(time_fit, *popt_quadratic)
pressure_fit_cubic = cubic(time_fit, *popt_cubic)
pressure_fit_quartic = quartic(time_fit, *popt_quartic)

# Print the coefficients in the desired format
# Print the coefficients in scientific notation
print(f"Linear fit: y = {popt_linear[0]:.2e}x + {popt_linear[1]:.2e}")
print(f"Quadratic fit: y = {popt_quadratic[0]:.2e}x^2 + {popt_quadratic[1]:.2e}x + {popt_quadratic[2]:.2e}")
print(f"Cubic fit: y = {popt_cubic[0]:.2e}x^3 + {popt_cubic[1]:.2e}x^2 + {popt_cubic[2]:.2e}x + {popt_cubic[3]:.2e}")
print(f"Quartic fit: y = {popt_quartic[0]:.2e}x^4 + {popt_quartic[1]:.2e}x^3 + {popt_quartic[2]:.2e}x^2 + {popt_quartic[3]:.2e}x + {popt_quartic[4]:.2e}")

# Plot the original data and the fitted curves
plt.scatter(time_numeric, pressure, label='Data', color='black')
plt.plot(time_fit, pressure_fit_linear, label='Linear fit', color='blue')
plt.plot(time_fit, pressure_fit_quadratic, label='Quadratic fit', color='red')
plt.plot(time_fit, pressure_fit_cubic, label='Cubic fit', color='green')
plt.plot(time_fit, pressure_fit_quartic, label='Quartic fit', color='purple')
plt.xlabel('Time (seconds)')
plt.ylabel('Pressure')
plt.legend()
plt.show()


