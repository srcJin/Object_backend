import time
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from the environment variable
api_key_1 = os.getenv("OPENAI_API_KEY_1")
api_key_2 = os.getenv("OPENAI_API_KEY_2")

client1 = OpenAI(api_key=api_key_1)
client2 = OpenAI(api_key=api_key_2)


def gpt_call(system_prompt, user_input):
    """
    Generic function to call the GPT model with a system prompt and user input.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]

    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo",
    )
    return response.choices[0].message.content


def refine_argument(text, style="professional"):
    """
    Refines the given text into a more professional form using GPT.
    """
    return gpt_call(
        f"Refine the following text into a {style} form, maximum 15 words:", text
    )


def simulate_debate(text1, text2, rounds):
    """
    Simulates a debate for a specified number of rounds.
    """
    transcript1 = text1  # Initial statement for Agent 1
    transcript2 = text2  # Initial statement for Agent 2
    current = text1
    opponent = text2

    for _ in range(rounds):
        new_turn = gpt_call(
            "You are a great debator, Continue the debate, maximum 15 words:", current
        )
        if current == text1:
            transcript1 += " " + new_turn
            current_transcript = transcript1
            opponent_transcript = transcript2
        else:
            transcript2 += " " + new_turn
            current_transcript = transcript2
            opponent_transcript = transcript1

        yield (current_transcript, opponent_transcript)
        current, opponent = opponent, new_turn


def display_state(ch1, ch2, ch3, ch4):
    """
    Displays the state of all four channels.
    """
    print(f"Channel 1: {ch1}")
    print(f"Channel 2: {ch2}")
    print(f"Channel 3: {ch3}")
    print(f"Channel 4: {ch4}")
    print()
    time.sleep(1)


def generate_conclusions(transcript1, transcript2):
    """
    Generates one-line conclusions from the transcripts of both agents.
    """
    conclusion1 = gpt_call("Summarize the following debate in one line:", transcript1)
    conclusion2 = gpt_call("Summarize the following debate in one line:", transcript2)
    return conclusion1, conclusion2


def main():
    user1_input = input("请输入第一位用户的内容: ")
    user2_input = input("请输入第二位用户的内容: ")

    user1_refined = refine_argument(user1_input)
    user2_refined = refine_argument(user2_input)

    rounds = int(input("请输入辩论回合数: "))

    # Display initial state
    display_state(user1_input, user1_refined, user2_refined, user2_input)

    # Simulate debate and display state after each round
    debate_transcript = []
    for current_transcript1, current_transcript2 in simulate_debate(
        user1_refined, user2_refined, rounds
    ):
        display_state(
            user1_input, current_transcript1, current_transcript2, user2_input
        )
        debate_transcript.append((current_transcript1, current_transcript2))

    # Generate conclusions
    conclusion1, conclusion2 = generate_conclusions(*debate_transcript[-1])

    # Display final state with conclusions
    display_state(
        conclusion1, debate_transcript[-1][0], debate_transcript[-1][1], conclusion2
    )


if __name__ == "__main__":
    main()
