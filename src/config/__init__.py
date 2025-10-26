import pathlib
import sys
import time
import logging
import tomli  # type: ignore
from functools import wraps

from src.config.ColorFormatter import ColorFormatter


# --------------------------------------- Load Configuration ---------------------------------------
path = pathlib.Path(__file__).parent.parent.parent / "config.toml"
with path.open(mode="rb") as fp:
    _conf = tomli.load(fp)
    print(_conf)


# --------------------------------------- Logger Stream Handler ---------------------------------------
# - Create a stream handler to handle colorized logging output
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(ColorFormatter("%(levelname)s: %(message)s"))

ROOT_DIR = str(pathlib.Path(__file__).parent.parent)

l_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | [%(name)s@%(funcName)s] | %(message)s",
    "%Y-%m-%d " "%H:%M:%S",
)


stream_handler.setFormatter(l_formatter)

# File handler for logging to a file
f_handler = logging.FileHandler("app.log")
f_handler.setLevel(logging.DEBUG)
f_handler.setFormatter(l_formatter)


# --------------------------------------- get_config ---------------------------------------
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


# --------------------------------------- get_enabled_commands ---------------------------------------
# - Get a list of enabled commands from the configuration
def get_enabled_commands():
    return get_config("general", "enabled_commands")


# --------------------------------------- get_genres ---------------------------------------
def get_genre_mapping():
    return get_config("general", "GENRE_MAPPING")


# --------------------------------------- get_supported_formats ---------------------------------------
def get_supported_formats():
    return get_config("general", "SUPPORTED_FORMATS")


# --------------------------------------- get_logger ---------------------------------------
# - Create a logger with colored output
def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Remove any existing handlers to avoid duplicate logs
    if logger.handlers:
        logger.handlers.clear()

    # Create and configure colored stream handler
    color_formatter = ColorFormatter("%(levelname)s: %(message)s")
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(color_formatter)

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


# --------------------------------------- show_me_time ---------------------------------------
# - Decorator to log the execution time of a function
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
