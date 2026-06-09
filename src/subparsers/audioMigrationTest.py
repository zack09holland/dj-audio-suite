import time
import random

from colorama import Fore, Style
from src.config import get_logger

logger = get_logger(__name__)

_SOURCE = "/mnt/c/Users/zack09holland/Downloads/refined-audio/"
_DEST   = "/mnt/c/Users/zack09holland/Music/Categories/"

FAKE_FILES = [
    {"filename": "Fedde Le Grand ft. Ida Corr - Let Me Think About It (Dunisco Remix).m4a", "genre": "Tech House"},
    {"filename": "Gapless - Gas.m4a",                                                        "genre": "Tech House"},
    {"filename": "Danny Tenaglia & Celeda - Music Is The Answer (Mike Vale Edit).m4a",       "genre": "House"},
    {"filename": "Chris Stussy - Body & Soul.m4a",                                           "genre": "Deep House"},
    {"filename": "Jamie Jones - Your Love.m4a",                                              "genre": "Tech House"},
    {"filename": "HardFi - Hard To Beat (Route 94 Edit).m4a",                               "genre": "House"},
    {"filename": "Solardo - Trespass.m4a",                                                   "genre": "Tech House"},
    {"filename": "Bicep - Glue.m4a",                                                         "genre": "House"},
    {"filename": "Denis Sulta - Pure Gram Pish.m4a",                                        "genre": "Tech House"},
    {"filename": "Amelie Lens - Exhale.m4a",                                                "genre": "Techno"},
    {"filename": "Charlotte de Witte - Doppler.m4a",                                        "genre": "Hard Techno"},
    {"filename": "Fisher - Losing It.m4a",                                                   "genre": "Tech House"},
    {"filename": "Drake - God's Plan.m4a",                                                   "genre": "Hip Hop"},
    {"filename": "Unknown Track.m4a",                                                        "genre": None},
    {"filename": "Bicep - Glue (Club Mix).m4a",                                             "genre": "House"},
    {"filename": "Dixon - Oblique.m4a",                                                      "genre": "Deep House"},
    {"filename": "Solomun - Customer Is King.m4a",                                           "genre": "Melodic House & Techno"},
    {"filename": "Four Tet - Baby.m4a",                                                      "genre": "Electronic"},
    {"filename": "J. Cole - No Role Modelz.m4a",                                             "genre": "Hip Hop"},
    {"filename": "Peggy Gou - Starry Night.m4a",                                             "genre": "Tech House"},
]

GENRE_FOLDER_MAP = {
    "Tech House":            "House/Tech House",
    "House":                 "House",
    "Deep House":            "House/Deep House",
    "Techno":                "Techno",
    "Hard Techno":           "Techno",
    "Hip Hop":               "Hip Hop",
    "Electronic":            "Electronic",
    "Melodic House & Techno":"House/Melodic House & Techno",
}


# ─── Main command ────────────────────────────────────────────────────────────

def run_audio_migration_test(args):
    transfer_type = "move"  # default for display purposes
    genre_counts: dict[str, int] = {}
    processed = 0

    logger.info(f"Starting music migration from {_SOURCE} to {_DEST}")

    for entry in FAKE_FILES:
        filename = entry["filename"]
        genre    = entry["genre"]
        src_path = f"{_SOURCE}{filename}"

        time.sleep(random.uniform(0.05, 0.15))

        if not genre:
            logger.warning(f"No genre found for {filename}")
            continue

        genre_folder = GENRE_FOLDER_MAP.get(genre, "Unknown")
        full_dest    = f"{_DEST}{genre_folder}"
        dest_path    = f"{full_dest}/{filename}"

        genre_counts[genre] = genre_counts.get(genre, 0) + 1
        processed += 1

        logger.info(
            f"{Fore.CYAN}Moved{Style.RESET_ALL} {filename} -> {full_dest}"
        )

    # Summary
    print("\nGenre Counts:")
    for genre, count in sorted(genre_counts.items()):
        print(f"{Fore.BLUE}{genre}:{Style.RESET_ALL} {count}")
    print(f"\nTotal files processed: {processed}")
    logger.info("Audio migration complete.")


# ─── Subparser ───────────────────────────────────────────────────────────────

def create_subparser(subparsers):
    parser = subparsers.add_parser(
        "audioMigrationTest",
        help="Simulate audioMigration command output without moving real files",
        aliases=["am-test", "test-am"],
    )
    parser.set_defaults(func=run_audio_migration_test)
