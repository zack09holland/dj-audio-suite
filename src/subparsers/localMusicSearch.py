import os
import subprocess
from src.config import get_logger

logger = get_logger(__name__)


# --------------------------------------- local_music_search ---------------------------------------
#  - Continuous search for music files by artist or song name
def local_music_search(args):

    search_term = args.get("search_term")
    music_dir = args.get("music_dir") if args.get("music_dir") else "."

    if not os.path.exists(music_dir):
        logger.error(f"Music directory {music_dir} does not exist")
        return

    # If initial search term was provided
    if search_term:
        _perform_search(search_term, music_dir)

    # Enter interactive mode
    logger.info("\nEnter search terms (artist/song) or 'quit' to exit:")
    while True:
        try:
            user_input = input("> ").strip().lower()

            if user_input in ("quit", "exit", "q"):
                logger.info("Exiting search mode...")
                break

            if user_input:
                _perform_search(user_input, music_dir)

        except KeyboardInterrupt:
            logger.info("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Search error: {e}")


# --------------------------------------- _perform_search ---------------------------------------
def _perform_search(search_term: str, base_dir: str):
    """Execute the find command and display results"""
    try:
        # Construct and execute find command
        command = [
            "find",
            base_dir,
            "-type",
            "f",
            "-iname",
            f"*{search_term}*",
            "-o",
            "-iname",
            f"*{search_term}*",
        ]

        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Process results
        if result.returncode == 0:
            files = result.stdout.splitlines()
            if files:
                logger.info(f"\nFound {len(files)} results for '{search_term}':")
                for file in files:
                    logger.info(f" - {file}")
            else:
                logger.info(f"No results found for '{search_term}'")
        else:
            logger.error(f"Search failed: {result.stderr}")

    except Exception as e:
        logger.error(f"Error performing search: {e}")


# --------------------------------------- create_subparser ---------------------------------------
def create_subparser(subparsers):
    command_parser = subparsers.add_parser(
        "localMusicSearch",
        help="Search local directory for song or artist",
        aliases=["local-music-search", "local-search", "search"],
    )

    # Optional arguments
    command_parser.add_argument(
        "--search-term", "-s", default=None, help="Initial search term to start with"
    )

    command_parser.add_argument(
        "--music-dir",
        "-d",
        default=".",
        help="Base directory to search from (default: current directory)",
    )

    command_parser.set_defaults(func=local_music_search)
