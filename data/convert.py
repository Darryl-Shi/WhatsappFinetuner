import argparse
import datetime
import pandas as pd
from collections import defaultdict
import re
from pathlib import Path
GENERAL_WA_MULTI_SEARCH_PATTERN = r'^(.*?):(.*)'
LINE_SPLIT_DELIMITER = "\n"

def remove_timestamps(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        
        # Remove timestamps
        text = re.sub(r'\[\d+/\d+/\d+, \d+:\d+:\d+ (AM|PM)\] ', '', text)
        
        #remove [U+200E] characters
        text = re.sub(r'\u200e', '', text)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

def text_to_dictionary(text, prompt, response):
    """
    Converts a whatsapp chat into a prompt and
    response dataframe for the purposes of finetuning.
    :param text:
    :param prompt:
    :param response:
    :return:
    """
    text_list = text.split('\n')
    result_dict, count, prev_author = defaultdict(dict), 0, ''
    for line in text_list:
        search_pattern = re.search(GENERAL_WA_MULTI_SEARCH_PATTERN, line)
        if search_pattern is not None:
            author = search_pattern.group(1)
            message = search_pattern.group(2).strip().replace('"', '')
            if author == prompt:
                if author == prev_author:
                    prev = result_dict[count]['prompt'][:-7]
                    result_dict[count]['prompt'] = f"{prev}. {message}\n\n###\n\n"
                else:
                    count += 1
                    result_dict[count].update({'prompt': message + "\n\n###\n\n"})
            elif author == response:
                if author == prev_author:
                    prev = result_dict[count]['completion'][:-4]
                    result_dict[count]['completion'] = f"{prev}. {message} ###"
                else:
                    result_dict[count].update({'completion': message + " ###"})
            prev_author = author
    return result_dict

def parse_whatsapp_text_into_dataframe(raw_text, prompter, responder):
    result_dict = text_to_dictionary(raw_text, prompter, responder)
    df = pd.DataFrame.from_dict(result_dict, orient='index')
    
    if 'prompt' not in df.columns or 'completion' not in df.columns:
        return pd.DataFrame(columns=['prompt', 'completion'])  # return empty df with correct columns
    else:
        return df[['prompt', 'completion']].dropna()



def converter(
        filepath: str,
        prompter: str,
        responder: str,
) -> pd.DataFrame:
    """
    Turn whatsapp chat data into a format
    that can be trained by openai's fine tuning api.
    :param file: Path to file we want to convert
    :param prompter: The person to be labelled as the prompter
    :param responder: The person to be labelled as the responder
    :return: a parsed pandas dataframe
    """
    remove_timestamps(filepath)
    with open(filepath, 'r', encoding="utf-8") as fp:
        text = fp.read()
    df = parse_whatsapp_text_into_dataframe(text, prompter, responder)
    df = df.dropna()
    return df

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

    save_file = filename if filename else datetime.datetime.now()
    converter(path, prompter, responder).to_json(f'output_{save_file}.json',lines=False,orient='records', force_ascii=False)


