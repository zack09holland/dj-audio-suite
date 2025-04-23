import logging
from colorama import Fore, Style


# --------------------------------------- Color Formatter ---------------------------------------
# Define a custom formatter with colors
class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.MAGENTA,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA,
        "[youtube]": Fore.RED,
        "[soundcloud]": Fore.GREEN,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, "")
        reset = Style.RESET_ALL

        # Color the level name (e.g., ERROR, INFO, DEBUG)
        record.levelname = f"{log_color}{record.levelname}{reset}"
        return super().format(record)

    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith("[debug] "):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
