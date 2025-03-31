import pathlib
from pathlib import Path
import tomli
import logging
from functools import wraps
import time
from logging import StreamHandler, FileHandler
from colorama import Fore, Style
import sys

path = pathlib.Path(__file__).parent.parent.parent / "config.toml"
with path.open(mode="rb") as fp:
    _conf = tomli.load(fp)
    print(_conf)


# Define a custom formatter with colors
class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, "")
        reset = Style.RESET_ALL

        # Color the level name (e.g., ERROR, INFO, DEBUG)
        record.levelname = f"{log_color}{record.levelname}{reset}"
        return super().format(record)


# Create a stream handler with color support
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(ColoredFormatter("%(levelname)s: %(message)s"))


def get_config(section: str, p_name: str = None, default_value=None):
    if section not in _conf.keys():
        raise ValueError(f'Invalid config value given "{section}"')

    config_data = _conf[section]

    keys = p_name.split(".") if p_name else []

    for key in keys:
        if config_data and key in config_data.keys():
            config_data = config_data.get(key)
        else:
            config_data = None
    return config_data if config_data else default_value


# def get_env_nodes(env: str):
#     nodes = get_config("envs_nods", env)
#     return nodes if nodes else []


# def get_envs():
#     return list(get_config("envs_nods").keys())


def get_enabled_commands():
    return get_config("general", "enabled_commands")


def get_available_dump_format():
    return ["p", "d", "t", "c"]


ROOT_DIR = str(Path(__file__).parent.parent)

l_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | [%(name)s@%(funcName)s] | %(message)s",
    "%Y-%m-%d " "%H:%M:%S",
)

stream_handler = StreamHandler()
# stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(l_formatter)

f_handler = FileHandler("app.log")
f_handler.setLevel(logging.DEBUG)
f_handler.setFormatter(l_formatter)


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Remove any existing handlers to avoid duplicate logs
    if logger.handlers:
        logger.handlers.clear()

    # Create and configure colored stream handler
    colored_formatter = ColoredFormatter("%(levelname)s: %(message)s")
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(colored_formatter)

    # Add the colored handler
    logger.addHandler(stream_handler)

    # Optionally add file handler (uncomment if needed)
    # f_handler = FileHandler("app.log")
    # f_handler.setLevel(logging.DEBUG)
    # f_handler.setFormatter(l_formatter)
    # logger.addHandler(f_handler)

    # Prevent propagation to root logger to avoid duplicate logs
    logger.propagate = False

    return logger


def show_me_time(app_logger):
    def timely(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            app_logger.info(
                "{} ran in {}s".format(func.__name__, round(end - start, 2))
            )
            return result

        return wrapper

    return timely
