import re
import pandas as pd
from pathlib import Path
import src.config as config
import src.aws as aws
from src.logger import get_logger
_logger = get_logger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[1]
data_folder = f"{ROOT_DIR}/data/"

env = config.get_config().env

def sanitize_search_input(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.strip()[:100]
    if not re.match(r"^[a-zA-Z\s\-']*$", text):
        return ""
    return text


def get_asset(file: str) -> pd.DataFrame:
    _logger.info("Loading asset: %s (env=%s)", file, env)
    try:
        if env == "dev":
            df = pd.read_csv(data_folder + file)
        else:  # PROD
            df = aws.get_s3_file(file)
        _logger.info("Successfully loaded asset: %s (%d rows)", file, len(df))
        return df
    except Exception as e:
        _logger.error("Failed to load asset '%s': %s", file, e)
        raise

