import re
import pandas as pd
from pathlib import Path
import src.config as config
import src.aws as aws

ROOT_DIR = Path(__file__).resolve().parents[1]
data_folder = f"{ROOT_DIR}/data/"

env = config.get_config().env

def get_asset(file: str) -> pd.DataFrame:
    if env == "dev":
        return pd.read_csv(data_folder + file)
    else: # PROD
        return aws.get_s3_file(file)
