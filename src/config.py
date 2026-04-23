import os
from dataclasses import dataclass
import getpass
from dotenv import load_dotenv, find_dotenv


@dataclass
class BaseConfig:
    """Settings common to all environments."""

    # Generic app settings
    APP_NAME: str = "reality-stats"
    # Logging
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")

@dataclass
class DevConfig(BaseConfig):
    """Development configuration."""
    env: str = "dev"
    DEBUG: bool = True
    TESTING: bool = True

@dataclass
class ProdConfig(BaseConfig):
    """Production configuration."""
    env: str = "prod"
    DEBUG: bool = False
    TESTING: bool = False

def get_config():
    env_file = find_dotenv()
    load_dotenv(env_file)

    if os.getenv('APP_ENV') == 'dev':
        return DevConfig()
    else:
        return ProdConfig()


