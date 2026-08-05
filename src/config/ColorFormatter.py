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
        msg_color = ""

        # Override color for specific message patterns
        if record.levelname == "INFO" and str(record.msg).startswith("Already exists, skipping:"):
            log_color = Fore.YELLOW
            msg_color = Fore.YELLOW
        elif record.levelname == "INFO" and str(record.msg).startswith("Successfully downloaded"):
            msg_color = Fore.GREEN

        reset = Style.RESET_ALL

        # Color the level name (e.g., ERROR, INFO, DEBUG)
        record.levelname = f"{log_color}{record.levelname}{reset}"

        # Color the message text where needed
        if msg_color:
            record.msg = f"{msg_color}{record.msg}{reset}"

        return super().format(record)
