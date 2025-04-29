from tinytag import TinyTag  # type: ignore
import os
import shutil
from colorama import init, Fore, Style
from src.config import get_logger

# Initialize colorama and logger
init()
logger = get_logger(__name__)

# Constants
DEFAULT_SOURCE = "/mnt/c/Users/zack09holland/Downloads/refined-audio/"
DEFAULT_DESTINATIONS = [
    "/mnt/c/Users/zack09holland/Music/Categories/",
    # "/mnt/m/Categories/",
]
SUPPORTED_FORMATS = (".mp3", ".m4a", ".flac", ".wav", ".opus")

# Genre to folder mapping
GENRE_MAPPING = {
    "House": "House",
    "Bass House": "House/Bass House",
    "Afro House": "House/Afro House",
    "Funky House": "House/Funky House",
    "Latin House": "House/Latin House",
    "Latin Tech House": "House/Latin House",
    "Tech House": "House/Tech House",
    "Deep House": "House/Deep House",
    "Progressive House": "House/Progressive House",
    "Melodic House & Techno": "House/Melodic House & Techno",
    "Hip Hop House": "House/Hip Hop House",
    "Hip Hop": "Hip Hop",
    "Drum & Bass": "Drum and Bass",
    "Dubstep": "Electronic",
    "Dance & EDM": "Electronic",
    "Electronic": "Electronic",
    "Mainstage": "Electronic",
    "Indie Dance": "Dance",
    "Dance / Electro Pop": "Dance",
    "Dance": "Dance",
    "Hard Techno": "Techno",
    "Techno": "Techno",
    "Rap": "Hip Hop",
}

# --------------------------------- get_genre ---------------------------------
def get_genre(file_path):
    """Extract genre metadata from audio file"""
    try:
        audio = TinyTag.get(file_path)
        if audio and audio.genre:
            logger.debug(f"Genre found: {audio.genre}")
            return audio.genre
        return None
    except Exception as e:
        logger.error(f"Error reading metadata for {file_path}: {e}")
        return None

# --------------------------------- get_genre_folder ---------------------------------
def get_genre_folder(genre):
    """Map genre to folder path"""
    return GENRE_MAPPING.get(genre, "Unknown")

# --------------------------------- ensure_directory_exists ---------------------------------
def ensure_directory_exists(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Created directory: {path}")

# --------------------------------- process_file ---------------------------------
def process_file(file_path, destinations, transfer_type):
    """Process individual music file and move/copy to destination(s)."""
    genre = get_genre(file_path)
    if not genre:
        logger.warning(f"No genre found for {os.path.basename(file_path)}")
        return False

    filename = os.path.basename(file_path)
    first = True  # For move-once logic

    for dest in destinations:
        genre_folder = get_genre_folder(genre)
        full_dest = os.path.join(dest, genre_folder)
        ensure_directory_exists(full_dest)

        dest_file_path = os.path.join(full_dest, filename)

        if transfer_type == "move" and first:
            shutil.move(file_path, dest_file_path)
            logger.info(f"{Fore.CYAN}Moved{Style.RESET_ALL} {filename} to {full_dest}")
            first = False
        elif transfer_type == "copy":
            shutil.copy(file_path, dest_file_path)
            logger.info(f"{Fore.CYAN}Copied{Style.RESET_ALL} {filename} to {full_dest}")
        elif transfer_type == "both":
            if first:
                shutil.move(file_path, dest_file_path)
                logger.info(f"{Fore.CYAN}Moved{Style.RESET_ALL} {filename} to {full_dest}")
                first = False
            else:
                shutil.copy(os.path.join(destinations[0], genre_folder, filename), dest_file_path)
                logger.info(f"{Fore.CYAN}Copied{Style.RESET_ALL} {filename} to {full_dest}")

    return True


# --------------------------------- move_music_by_genre ---------------------------------
def move_music_by_genre(args):
    """Main function to organize music files by genre"""
    source = args.get("source") or DEFAULT_SOURCE
    destinations = args.get("destinations") or DEFAULT_DESTINATIONS
    transfer_type = args.get("transferType")

    if not os.path.exists(source) or not os.path.isdir(source):
        logger.error(f"Invalid source path: {source}")
        return

    genre_counts = {}
    processed_files = 0
    
    logger.info(f"Starting music migration from {source} to {destinations[0]} and {destinations[1]}")
    
    # Loop through all files in the source directory
    for root, _, files in os.walk(source):
        for file in files:
            if file.lower().endswith(SUPPORTED_FORMATS):
                file_path = os.path.join(root, file)
                genre = get_genre(file_path)
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
                processed_files += 1
                process_file(file_path, destinations[0], destinations[1], transfer_type)

    # Print summary
    print("\nGenre Counts:")
    for genre, count in sorted(genre_counts.items()):
        print(f"{Fore.BLUE}{genre}:{Style.RESET_ALL} {count}")
    print(f"Total files processed: {processed_files}")

# --------------------------------- create_subparser ---------------------------------
def create_subparser(subparsers):
    """Create CLI subparser"""
    parser = subparsers.add_parser(
        "audioMigration",
        help="Organize music files by genre",
        aliases=["migrate", "audiomigrate", "am", "transfer", "move"],
    )

    parser.add_argument(
        "--source", help="Source directory containing music files"
    )
    parser.add_argument(
        "--destinations", nargs="+", help="Destination folders (primary and USB)"
    )
    parser.add_argument(
        "--transfer-type",
        choices=["move", "copy", "both"],
        help="Transfer operation: move, copy, or both",
    )

    parser.set_defaults(func=move_music_by_genre)
