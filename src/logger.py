import logging
from pathlib import Path
import src.config as config

ROOT_DIR = Path(__file__).resolve().parents[1]
_env = config.get_config().env

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    if _env == "dev":
        log_dir = ROOT_DIR / "logs"
        log_dir.mkdir(exist_ok=True)
        handler = logging.FileHandler(log_dir / "app.log")
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
