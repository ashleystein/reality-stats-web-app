import re
import pandas as pd
from pathlib import Path
from src.config import get_config
import src.aws as aws

ROOT_DIR = Path(__file__).resolve().parents[1]
data_folder = f"{ROOT_DIR}/data/"

env = get_config().env

def get_asset(file: str) -> pd.DataFrame:
    if env == "dev":
        return pd.read_csv(data_folder + file)
    else: # PROD
        return aws.get_s3_file(file)

# String cleaning
def clean_strings(raw_string, type=''):
    str_clean =  raw_string.text.replace('\n', '')
    if type == 'age':
        return str_clean
    else:
        return re.sub(r'^[^a-zA-Z]+|[^a-zA-Z]+$', '', str_clean)


def remove_leading_chars(orig_str, remove_char):
    text = orig_str.lower()
    new_text = text.lstrip(remove_char)
    return new_text.strip()

def remove_references(text: str):
    if not isinstance(text, str):
        return text
    pattern = r'\[([0-9]+|[a-z]+)\]'
    return re.sub(pattern, '', text)

def remove_weired_chars(text: str):
    if not isinstance(text, str):
        return text
    pattern = r'\[([0-9]+|[a-z]+)\]'
    return re.sub(pattern, '', text)


def does_file_exist(file_name):
    return Path(file_name).is_file()

def get_last_modified_time(file):

    file_path = Path(file)

    # Get the timestamp
    timestamp = file_path.stat().st_mtime

    return timestamp


