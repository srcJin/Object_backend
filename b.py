import time
from openai import OpenAI
import os
from dotenv import load_dotenv

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


def simulate_dialogue(client1, client2, user_input1, user_input2, rounds):
    """
    Simulates a dialogue between two GPT clients for a specified number of rounds.
    """
    # Initial messages for both clients, starting the conversation with user inputs
    messages_1 = [
        {
            "role": "system",
            "content": "You are a great debater, limit respond to 15 words.",
        },
        {"role": "user", "content": user_input1},
    ]
    messages_2 = [
        {
            "role": "system",
            "content": "You are a great debater, limit respond to 15 words.",
        },
        {"role": "user", "content": user_input2},
    ]

    for _ in range(rounds):
        # Client 1 generates a response
        new_turn_1 = gpt_call(client1, messages_1)
        messages_1.append({"role": "assistant", "content": new_turn_1})
        messages_2.append({"role": "user", "content": new_turn_1})

        # Client 2 generates a response
        new_turn_2 = gpt_call(client2, messages_2)
        messages_2.append({"role": "assistant", "content": new_turn_2})
        messages_1.append({"role": "user", "content": new_turn_2})

    return messages_1, messages_2


def display_conversation(conversation):
    """
    Displays the conversation.
    """
    for message in conversation:
        if message["role"] in ["user", "assistant"]:
            print(f"{message['role'].title()}: {message['content']}")
            print()


def main():
    rounds = int(input("Please enter the number of rounds for the debate: "))
    user_input1 = input("Please enter the starting statement for Agent 1: ")
    user_input2 = input("Please enter the starting statement for Agent 2: ")

    # Simulate dialogue and display the conversation from one side's perspective
    conversation_1, _ = simulate_dialogue(
        client1, client2, user_input1, user_input2, rounds
    )
    display_conversation(conversation_1)


if __name__ == "__main__":
    main()
