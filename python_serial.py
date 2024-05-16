import serial
import time
import sys
import glob

import serial.tools.list_ports


def list_serial_ports():
    """Lists serial port names

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of available serial ports
    """
    if sys.platform.startswith("win"):
        ports = ["COM" + str(i + 1) for i in range(256)]
    elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob("/dev/tty[A-Za-z]*")
    elif sys.platform.startswith("darwin"):
        ports = glob.glob("/dev/tty.*")
    else:
        raise EnvironmentError("Unsupported platform")

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def create_serial_connection(port, baud_rate):
    """Create and return a serial connection."""
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"Connected to {port} at {baud_rate} bps")
        return ser
    except serial.SerialException as e:
        print(f"Error: {e}")
        return None


def send_string_to_esp32(ser, text):
    """Sends a string to an ESP32 over a specified serial port."""
    if ser:
        try:
            ser.write((text + "\n").encode())  # Ensure proper line ending
            print("Message sent:", text)
            time.sleep(2)  # Wait for the ESP32 to process the data
        except serial.SerialException as e:
            print(f"Error during send: {e}")


def main():
    port = "COM6"  # adjust as necessary
    baud_rate = 9600
    messages = ["Hello ESP32S3_", "Second Message_"]

    # Create a serial connection
    ser = create_serial_connection(port, baud_rate)
    if ser:
        for message in messages:
            send_string_to_esp32(ser, message)
            time.sleep(2)  # Additional delay if needed between messages

        # Close the connection gracefully
        ser.close()
        print("Connection closed.")


if __name__ == "__main__":
    main()
