import serial, csv, time

def send_command(command_string):
    """Formats and sends a string command to the Arduino"""
    full_command = command_string + "\n"
    ser.write(full_command.encode('utf-8')) 
    
    print(f"Sent: {command_string}")

# for linux, the Arduino is usually connected to /dev/ttyACM0
arduino_port = "/dev/ttyACM0" 
baud_rate = 9600
output_file = "tst.csv"

# connect to arduino
ser = serial.Serial(arduino_port, baud_rate)
print(f"Connected to Arduino on {arduino_port}")

# Send quiet mode signal for datalogging
time.sleep(0.1)
ser.write(b'Q')
print("Sent Quiet Mode signal to setup()")

# wait for esc calibration and then send the test command
time.sleep(13)
send_command("test sweep")

# Open the CSV file to write data
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)

    try:
        while True:
            if ser.in_waiting > 0:
                # decode the incoming bytes to a string and strip any whitespace
                line = ser.readline().decode('utf-8').strip()
                print(line)
                
                writer.writerow([line])
                
    except KeyboardInterrupt:
        print("\nConnection stopped by user")
        send_command("st")
        ser.close()