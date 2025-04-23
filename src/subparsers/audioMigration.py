from tinytag import TinyTag
import os
import shutil
from colorama import init, Fore, Style
from src.config import get_logger

# Initialize colorama and logger
init()
logger = get_logger(__name__)

# Constants
DEFAULT_DESTINATIONS = [
    "/mnt/c/Users/zack09holland/Music/Categories/",
    "/mnt/m/Categories/",
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


def get_genre_folder(genre):
    """Map genre to folder path"""
    return GENRE_MAPPING.get(genre, "Unknown")


def ensure_directory_exists(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Created directory: {path}")


def process_file(file_path, base_dest, usb_dest, transfer_type):
    """Process individual music file"""
    genre = get_genre(file_path)
    if not genre:
        logger.warning(f"No genre found for {os.path.basename(file_path)}")
        return False

    genre_folder = get_genre_folder(genre)
    main_dest = os.path.join(base_dest, genre_folder)
    usb_dest_full = os.path.join(usb_dest, genre_folder)

    ensure_directory_exists(main_dest)
    ensure_directory_exists(usb_dest_full)

    filename = os.path.basename(file_path)

    if transfer_type == "move":
        shutil.move(file_path, os.path.join(main_dest, filename))
        logger.info(f"{Fore.CYAN}Moved{Style.RESET_ALL} {filename} to {main_dest}")
    elif transfer_type == "copy":
        shutil.copy(file_path, os.path.join(usb_dest_full, filename))
        logger.info(f"{Fore.CYAN}copied{Style.RESET_ALL} {filename} to {usb_dest_full}")
    else:  # Default is move + copy
        shutil.move(file_path, os.path.join(main_dest, filename))
        shutil.copy(
            os.path.join(main_dest, filename), os.path.join(usb_dest_full, filename)
        )
        logger.info(
            f"{Fore.CYAN}Moved{Style.RESET_ALL} {filename} to {main_dest} | {Fore.CYAN}copied{Style.RESET_ALL} to {usb_dest_full}"
        )

    return True


def move_music_by_genre(args):
    """Main function to organize music files by genre"""
    source = args.get("source")
    destinations = args.get("destinations") or DEFAULT_DESTINATIONS
    transfer_type = args.get("transferType")

    if not os.path.exists(source):
        logger.error(f"Source path does not exist: {source}")
        return

    if not os.path.isdir(source):
        logger.error(f"Source must be a directory: {source}")
        return

    if len(destinations) < 2:
        logger.warning("Only one destination provided, USB copy will be skipped")
        destinations.append(destinations[0])  # Use same folder for both

    genre_counts = {}
    processed_files = 0

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


def create_subparser(subparsers):
    """Create CLI subparser"""
    parser = subparsers.add_parser(
        "audioMigration",
        help="Organize music files by genre",
        aliases=["migrate", "audiomigrate", "am", "transfer"],
    )

    parser.add_argument(
        "--source", required=True, help="Source directory containing music files"
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
