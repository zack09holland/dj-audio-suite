import os
import sys


def windows_to_wsl_path(win_path):
    # Ensure the input path is absolute
    win_path = os.path.abspath(win_path)

    # Split the drive letter and the rest of the path
    drive, path = os.path.splitdrive(win_path)

    # Remove the colon from the drive and replace backslashes with forward slashes
    wsl_path = "/mnt/" + drive[:-1].lower() + path.replace("\\", "/")

    return wsl_path
