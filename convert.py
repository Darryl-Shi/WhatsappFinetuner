import argparse
import datetime
import pandas as pd
from collections import defaultdict
import re
from pathlib import Path
GENERAL_WA_MULTI_SEARCH_PATTERN = r'^(.*?):(.*)'
LINE_SPLIT_DELIMITER = "\n"
import json

def remove_timestamps(text):
    # Remove timestamps
    text = re.sub(r'\[\d+/\d+/\d+, \d+:\d+:\d+ (AM|PM)\] ', '', text)

    # remove [U+200E] characters
    text = re.sub(r'\u200e', '', text)

    return text

def convert_chat(original_chat, prompter, responder, chunk_index=None):
    converted_chat = {"messages": []}

    chat_lines = original_chat.split("\n")

    for line in chat_lines:
        if line.startswith(prompter):
            sender = "user"
        elif line.startswith(responder):
            sender = "assistant"
        else:
            continue

        content = line.split(": ", 1)[1]
        converted_chat["messages"].append({"role": sender, "content": content})

    return converted_chat


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process your whatsapp chat data.')
    parser.add_argument('--path', type=str, help='Path to file')
    parser.add_argument('--prompter', type=str, help='Name of Prompter')
    parser.add_argument('--responder', type=str, help='Name of Responder')
    parser.add_argument('--filename', type=str, help='Destination filename')

    args = parser.parse_args()
    path = args.path
    prompter = args.prompter
    responder = args.responder
    filename = args.filename

    save_file = filename if filename else str(datetime.datetime.now())
    with open(path, 'r+', encoding='utf-8') as f:
        original_chat = f.read()
        original_chat = remove_timestamps(original_chat)
        chat_lines = original_chat.split("\n")

        # Split chat into smaller chunks
        chunk_size = 2048
        chat_chunks = [chat_lines[i:i+chunk_size] for i in range(0, len(chat_lines), chunk_size)]

        for i, chunk in enumerate(chat_chunks):
            converted_chat = convert_chat("\n".join(chunk), prompter, responder, chunk_index=i+1)
            with open(f"{save_file}.jsonl", "a") as f:
                f.write(json.dumps(converted_chat) + "\n")
