import os
from mutagen.mp4 import MP4
from src.config import get_logger

from src.utils.metadata import clean_title_metadata

logger = get_logger(__name__)

# --------------------------------- clean_metadata ---------------------------------
def clean_metadata(args):
    """Edit title metadata in mp4 file by removing text before the first dash ('-')"""
    file_path = args.get("file")
    
    if not file_path or not os.path.isfile(file_path):
        logger.error(f"Invalid file path: {file_path}")
        return

    clean_title_metadata(file_path)

# --------------------------------- create_subparser ---------------------------------
def create_subparser(subparsers):
    command_parser = subparsers.add_parser(
        "clean-metadata",
        help="Edit .mp4 title metadata (remove text before first dash)",
        aliases=["clean", "edit"],
    )

    command_parser.add_argument(
        "--file",
        "-f",
        required=True,
        help="Path to the .mp4 file",
    )

    command_parser.set_defaults(func=clean_metadata)
