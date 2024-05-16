import time
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")


client = OpenAI(api_key=api_key)


def translate_text(text, target_language):
    """
    Uses OpenAI's GPT model to translate text into a target language.

    Args:
        text (str): The text to be translated.
        target_language (str): The target language (e.g., "English" or "French").

    Returns:
        str: The translated text.
    """
    messages = [
        {
            "role": "system",
            "content": f"You are a translator. Translate the following text to {target_language}.",
        },
        {"role": "user", "content": text},
    ]

    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo",
    )

    # Correctly extracting the 'content' from the response object
    translated_text = response.choices[
        0
    ].message.content  # Access the 'content' attribute directly
    return translated_text


def print_channel_output(channel_id, message):
    """
    Prints the output for a specified channel.

    Args:
        channel_id (int): The channel ID.
        message (str): The message to be printed.
    """
    print(f"Channel {channel_id}: {message}")


def main():
    # User input
    user1_input = input("请输入第一位用户的内容: ")
    user2_input = input("请输入第二位用户的内容: ")

    # Translate content
    user1_translated = translate_text(user1_input, "English")
    user2_translated = translate_text(user2_input, "French")

    # Configure the output for each channel
    channels = [
        {"channel_id": 1, "message": user1_input},
        {"channel_id": 2, "message": user1_translated},
        {"channel_id": 3, "message": user2_translated},
        {"channel_id": 4, "message": user2_input},
    ]

    # Sequentially output content for each channel
    for channel in channels:
        print_channel_output(channel["channel_id"], channel["message"])
        time.sleep(1)  # Time delay between each channel output


if __name__ == "__main__":
    main()
