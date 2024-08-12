import serial
import time
import csv
import os

sample_rate = 1

# Get the directory of the current Python file
file_directory = os.path.dirname(os.path.abspath(__file__))

# Ask the user for a file name
file_name = input("Please enter a name for the CSV file: ").strip()

# Wait until the user provides a non-empty file name
while not file_name:
    file_name = input("File name cannot be empty. Please enter a name for the CSV file: ").strip()

# Get the current date and time
start_time = time.strftime('%Y-%m-%d_%H-%M-%S')

# Construct the full path for the CSV file, appending the start time to the file name
csv_file_path = os.path.join(file_directory, f"{file_name}_{start_time}.csv")

# Configure the serial connection
ser = serial.Serial(
    port='COM4',  # Replace with your actual port
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=sample_rate
)

try:
    # Open serial port if not already open
    if not ser.is_open:
        ser.open()

    print("Serial port opened successfully")

    total_seconds = 0

    # Open the CSV file for writing
    with open(csv_file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Timestamp','Total Seconds', 'Pressure (Torr)'])  # Write header

        while True:
            # Send RD command to read the device
            ser.write('RD\r'.encode('ascii'))
            response = ser.readline().decode('ascii').strip()
            print(f"Response: {response}")

            # Write timestamp and response to the CSV file
            csvwriter.writerow([time.strftime('%Y-%m-%d %H:%M:%S'),total_seconds, response])
            csvfile.flush()  # Ensure data is written to the file
            total_seconds += sample_rate

            # Optional: Sleep for a bit if you want to space out the data collection

except serial.SerialException as e:
    print(f"Serial error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    ser.close()
    print("Serial connection closed")
