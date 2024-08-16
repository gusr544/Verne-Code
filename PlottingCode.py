import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

# Define the folder path containing the CSV files
folder_path = r'C:\Users\Gus\Desktop\Outgassing Code\Inhouse Tests'

# Get a list of all CSV files in the folder
csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

# Prepare lists to store data parts for plotting
all_part1_data = []
all_part2_data = []

# Returns the surface area of COPV coupon in m2
def rect(ds):
    return 2 * (ds[0] * ds[1] + ds[0] * ds[2] + ds[2] * ds[1]) / 1E6

# Surface areas in m2
surface_areas = [0.031685, 0.031685, rect([90, 105, 26]), rect([24, 106, 95]),rect([146,124,28]),rect([90,108,29]),rect([90,108,29]),rect([95,106,29]),rect([93,104,29]),rect([101,106,28])]
COPV_surface_area = 3.957
custom_labels = ["Control 1", "Control 2", "2hr Bake 1", "2hr Bake 2", "17hr Bake 1","17hr Bake 2","Molecular Sieve 1","Molecular Sieve 2","Low Outgassing Epoxy1","Low Outgassing Epoxy2"]
print(len(surface_areas))
print(len(custom_labels))
# Function to determine the pressure and time thresholds
def determine_thresholds(df):
    pressure_min = df['Pressure (Torr)'].min()
    pressure_threshold = max(pressure_min, 1E-4) + 1E-4
    time_threshold = 7200
    return pressure_threshold, time_threshold

# Function to split the data based on thresholds
def split_data(df, pressure_threshold, time_threshold):
    split_index = df[(df['Pressure (Torr)'] < pressure_threshold) | (df['Total Seconds'] >= time_threshold)].index[0]
    df_part1 = df.iloc[:split_index + 1]
    df_part2 = df.iloc[split_index + 1:]

    # Find where the pressure increases by 3*10^-4 Torr
    initial_pressure = df_part2['Pressure (Torr)'].iloc[0]
    increase_threshold = initial_pressure + 3e-4
    increase_index = df_part2[df_part2['Pressure (Torr)'] >= increase_threshold].index[0]

    # Adjust part 2 data to start from the increase point and reindex time
    df_part2 = df_part2.loc[increase_index:].copy()
    df_part2['Total Seconds'] = df_part2['Total Seconds'] - df_part2['Total Seconds'].iloc[0]

    df_part2 = df_part2[df_part2['Total Seconds'] <= 10800]

    return df_part1, df_part2

# Function to calculate the average rate of change per unit surface area
def calculate_average_rate_per_area(df_part2, surface_area):
    if len(df_part2) > 1:
        delta_pressure = df_part2['Pressure (Torr)'].iloc[-1] - df_part2['Pressure (Torr)'].iloc[0]
        delta_time = df_part2['Total Seconds'].iloc[-1] - df_part2['Total Seconds'].iloc[0]
        return (delta_pressure / delta_time) / surface_area
    else:
        return None


# Process each CSV file
for i, file in enumerate(csv_files):
    df = pd.read_csv(file)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])  # Convert to datetime if needed
    pressure_threshold, time_threshold = determine_thresholds(df)
    df_part1, df_part2 = split_data(df, pressure_threshold, time_threshold)

    # Filter df_part1 to include only data up to 10800 seconds
    df_part1 = df_part1[df_part1['Total Seconds'] <= 10800]

    # Add pressure per unit area column for df_part2
    df_part2['Pressure per Area (Torr/m^2)'] = df_part2['Pressure (Torr)'] / surface_areas[i]

    all_part1_data.append(df_part1)
    all_part2_data.append(df_part2)

    # Print the lowest pressure achieved
    lowest_pressure = df['Pressure (Torr)'].min()
    print(f'Lowest pressure achieved for {custom_labels[i]}: {lowest_pressure:.6e} Torr')

# Plot the pump down curve in the first figure
plt.figure(figsize=(8, 6))


# Plot all the first parts
for i, df_part1 in enumerate(all_part1_data):
    plt.plot(df_part1['Total Seconds'], df_part1['Pressure (Torr)'], label=custom_labels[i])
plt.xlabel('Total Seconds')
plt.ylabel('Pressure (Torr)')
plt.title('Pump Down Curve')
plt.grid(True)
plt.legend(loc='best')

plt.tight_layout(pad=3)
plt.show()

# Plot the outgassing and pressure per unit area curves in the second figure
plt.figure(figsize=(14, 10))

# Plot all the second parts - Outgassing Curve
plt.subplot(2, 1, 1)
for i, df_part2 in enumerate(all_part2_data):
    plt.plot(df_part2['Total Seconds'], df_part2['Pressure (Torr)'], label=custom_labels[i])

    # Calculate and print the average rate of outgassing per unit area
    average_rate_of_change_per_area = calculate_average_rate_per_area(df_part2, surface_areas[i])
    average_rate_of_change = average_rate_of_change_per_area * surface_areas[i] if average_rate_of_change_per_area is not None else None

    if average_rate_of_change is not None:
        print(f'Average rate of outgassing for {custom_labels[i]}: {average_rate_of_change*1000*60*60:.6f} mTorr/hour')
        print(f'Average rate of outgassing per unit area for {custom_labels[i]}: {average_rate_of_change_per_area*1000*60*60:.6f} mTorr/(hour*m^2)')
    else:
        print(f'Insufficient data points to calculate outgassing rate for {custom_labels[i]}')

plt.xlabel('Total Seconds')
plt.ylabel('Pressure (Torr)')
plt.title('Outgassing Curve')
plt.grid(True)

# Plot the pressure per unit area
plt.subplot(2, 1, 2)
for i, df_part2 in enumerate(all_part2_data):
    plt.plot(df_part2['Total Seconds'], df_part2['Pressure per Area (Torr/m^2)'], label=custom_labels[i])
plt.xlabel('Total Seconds')
plt.ylabel('Pressure per Area (Torr/m^2)')
plt.title('Pressure per Surface Area')
plt.grid(True)

plt.tight_layout(pad=3)
plt.figlegend(custom_labels, loc='upper center', ncol=len(custom_labels))

plt.show()
