import time
from openai import OpenAI
import os
from dotenv import load_dotenv

import serial
import sys
import glob

import serial.tools.list_ports


# Load environment variables from .env file
load_dotenv()

# Retrieve the API keys from the environment variables
api_key_1 = os.getenv("OPENAI_API_KEY_1")
api_key_2 = os.getenv("OPENAI_API_KEY_2")

client1 = OpenAI(api_key=api_key_1)
client2 = OpenAI(api_key=api_key_2)


def gpt_call(client, messages):
    """
    Function to call the GPT model with a list of messages.
    """
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo",
    )
    return response.choices[0].message.content


def refine_input(client, text):
    """
    Refines the given text using GPT model to a professional debate statement.
    """
    return gpt_call(
        client,
        [
            {
                "role": "system",
                "content": "Refine this into a professional debate statement, limit to 15 words. YOU MUST END YOUR RESPONSE WITH _",
            },
            {"role": "user", "content": text},
        ],
    )


def format_transcript(transcript):
    """
    Formats the transcript by numbering each point.
    """
    return "\n".join(
        f"Point {index + 1}: {point}" for index, point in enumerate(transcript)
    )


def simulate_dialogue(client1, client2, user_input1, user_input2, rounds):
    """
    Simulates a dialogue between two GPT clients for a specified number of rounds.
    """
    refined_input1 = refine_input(client1, user_input1)
    refined_input2 = refine_input(client2, user_input2)

    messages_1 = [
        {
            "role": "system",
            "content": "You are a debator, limit to 15 words. YOU MUST END YOUR RESPONSE WITH _",
        },
        {"role": "user", "content": refined_input1},
    ]
    messages_2 = [
        {
            "role": "system",
            "content": "You are a debator, limit to 15 wordss. YOU MUST END YOUR RESPONSE WITH _",
        },
        {"role": "user", "content": refined_input2},
    ]

    transcript1 = [refined_input1]
    transcript2 = [refined_input2]

    for _ in range(rounds):
        new_turn_1 = gpt_call(client1, messages_1)
        transcript1.append(new_turn_1)
        messages_1.append({"role": "assistant", "content": new_turn_1})
        messages_2.append({"role": "user", "content": new_turn_1})

        new_turn_2 = gpt_call(client2, messages_2)
        transcript2.append(new_turn_2)
        messages_2.append({"role": "assistant", "content": new_turn_2})
        messages_1.append({"role": "user", "content": new_turn_2})

        # Display the state after each round
        display_state(refined_input1, new_turn_2, refined_input2, new_turn_1)

    # Generate conclusions
    conclusion1 = gpt_call(
        client1,
        [
            {
                "role": "system",
                "content": "Output Start with [Summarize], Summarize the debate from your argument in 15 words, did you lose?",
            },
            {"role": "user", "content": " ".join(transcript1)},
        ],
    )
    conclusion2 = gpt_call(
        client2,
        [
            {
                "role": "system",
                "content": "Output Start with [Summarize], Summarize the debate from your argument in 15 words. YOU MUST END YOUR RESPONSE WITH _  ",
            },
            {"role": "user", "content": " ".join(transcript2)},
        ],
    )

    return (
        refined_input1,
        format_transcript(transcript1),
        refined_input2,
        format_transcript(transcript2),
    )


def display_state(agent1_front, agent1_back, agent2_front, agent2_back, baud_rate=9600):
    """
    Displays the state of all four channels.
    """
    print(f"Agent 1 Front: {agent1_front}")
    print(f"Agent 1 Back: {agent1_back}")
    print(f"Agent 2 Front: {agent2_front}")
    print(f"Agent 2 Back: {agent2_back}")
    print()

    # send the data to esp32
    data = [agent1_front, agent1_back, agent2_front, agent2_back]
    display_state_to_esp32s(ports, data, baud_rate)
    time.sleep(1)


def display_state_to_esp32s(ports, data, baud_rate=9600):
    """
    Sends the state data to ESP32 devices specified in the ports list.

    Args:
        ports (list of str): List of serial ports for each ESP32 device.
        data (list of str): List of data strings to send to each ESP32 device.
        baud_rate (int): Baud rate for the serial communication.
    """
    for port, text in zip(ports, data):
        send_string_to_esp32(port, baud_rate, text)


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


def send_string_to_esp32(port, baud_rate, text):
    """
    Sends a string to an ESP32S3 over a specified serial port.

    Args:
    port (str): The serial port to connect to (e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux).
    baud_rate (int): The baud rate for the serial communication.
    text (str): The text string to send to the ESP32S3.
    """
    try:
        # Open the serial port
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            print(f"Connected to {port} at {baud_rate} bps")

            # Send the string as bytes
            ser.write(text.encode())
            print("Message sent:", text)

            # Wait for the ESP32 to process the data
            time.sleep(1)

            # Optionally, read response from ESP32
            while ser.in_waiting:
                response = ser.read(ser.in_waiting).decode("utf-8")
                print("Received response:", response)

    except serial.SerialException as e:
        print(f"Error: {e}")


def list_avaliable_ports():
    # Display the list of available ports
    print("Available serial ports:")
    for port in list_serial_ports():
        print(port)


def main():
    rounds = int(input("Number of rounds: "))
    user_input1 = input("Starting statement for Agent 1: ")
    user_input2 = input("Starting statement for Agent 2: ")

    # Display initial state
    refined_input1 = refine_input(client1, user_input1)
    refined_input2 = refine_input(client2, user_input2)
    display_state(user_input1, refined_input1, user_input2, refined_input2)

    # Simulate dialogue and display the final state
    conclusion1, full_transcript1, conclusion2, full_transcript2 = simulate_dialogue(
        client1, client2, user_input1, user_input2, rounds
    )

    # Display final state with conclusions
    display_state(conclusion1, full_transcript1, conclusion2, full_transcript2)


if __name__ == "__main__":

    ports = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3"]

    list_avaliable_ports()
    main()
