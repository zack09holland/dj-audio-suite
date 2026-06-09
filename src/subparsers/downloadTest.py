import sys
import time
import random

from colorama import Fore, Style
from src.config import get_logger

logger = get_logger(__name__)

_BAR_WIDTH = 40
_OUTPUT_DIR = "/mnt/c/Users/zack09holland/Downloads/downloaded"

FAKE_TRACKS = [
    {
        "artist": "Fedde Le Grand ft. Ida Corr",
        "title": "Let Me Think About It (Dunisco Remix)",
        "source": "soundcloud",
    },
    {
        "artist": "Gapless",
        "title": "Gas",
        "source": "soundcloud",
    },
    {
        "artist": "Danny Tenaglia & Celeda",
        "title": "Music Is The Answer (Mike Vale Edit)",
        "source": "soundcloud",
    },
    {
        "artist": "Omri & Rafael",
        "title": "Little Kitty",
        "source": "soundcloud",
        "error": True,
    },
    {
        "artist": "Hot Creations",
        "title": "Deep In The Night (Extended Mix)",
        "source": "soundcloud",
        "skip": True,
    },
    {
        "artist": "Chris Stussy",
        "title": "Body & Soul",
        "source": "soundcloud",
    },
]

_PP_STEPS = [
    (80.0,  85.0, "Fixing container"),
    (85.0,  90.0, "Extracting audio"),
    (90.0,  95.0, "Writing metadata"),
    (95.0, 100.0, "Embedding thumbnail"),
]


# ─── Progress bar helpers (mirrors ytDownloader) ────────────────────────────

def _draw(pct: float, suffix: str = ""):
    filled = int(_BAR_WIDTH * pct / 100)
    bar = (
        Fore.GREEN + "█" * filled
        + Style.DIM + "░" * (_BAR_WIDTH - filled)
        + Style.RESET_ALL
    )
    line = f"\r  [{bar}] {Fore.CYAN}{pct:5.1f}%{Style.RESET_ALL}"
    if suffix:
        line += f"  {suffix}"
    sys.stdout.write(line.ljust(120))
    sys.stdout.flush()


def _draw_complete():
    filled = "█" * _BAR_WIDTH
    sys.stdout.write(
        f"\r  [{Fore.GREEN}{filled}{Style.RESET_ALL}]"
        f" {Fore.GREEN}100.0%{Style.RESET_ALL}  Done!".ljust(120) + "\n"
    )
    sys.stdout.flush()


# ─── Simulate a single track download ───────────────────────────────────────

def _simulate_download(track):
    filename = f"{track['artist']} - {track['title']}"
    outtmpl = f"{_OUTPUT_DIR}/{filename}.%(ext)s"
    url = f"https://{track['source']}.com/{track['artist'].lower().replace(' ', '-')}/{track['title'].lower().replace(' ', '-')}"

    logger.info(f"Downloading {url} to {outtmpl}")
    logger.info(f"  -> Saving to: {_OUTPUT_DIR}/{filename}.m4a")

    # Simulate fragment-based download (HLS style, 0-80% of bar)
    total_frags = random.randint(12, 20)
    for frag in range(1, total_frags + 1):
        dl_pct = (frag / total_frags) * 100
        overall = dl_pct * 0.80
        speed = f"{random.uniform(1.8, 3.2):.2f}MiB/s"
        remaining_frags = total_frags - frag
        eta_secs = max(0, int(remaining_frags * 0.12))
        eta = f"0:00:{eta_secs:02d}"
        _draw(overall, f"{speed}  eta {eta}")
        time.sleep(0.06)

    _draw(80.0, "Post-processing...")
    time.sleep(0.25)

    # Simulate post-processing steps
    for start_pct, end_pct, label in _PP_STEPS:
        _draw(start_pct, f"{label}...")
        time.sleep(random.uniform(0.3, 0.6))
        if end_pct >= 100.0:
            _draw_complete()
        else:
            _draw(end_pct)
        time.sleep(0.05)

    logger.info(f"Successfully downloaded: {outtmpl}")


# ─── Main command ────────────────────────────────────────────────────────────

def run_download_test(args):
    logger.info(f"Starting download — {len(FAKE_TRACKS)} tracks queued")

    for track in FAKE_TRACKS:
        if track.get("error"):
            logger.error(
                f"[{track['source']}] Unable to download JSON metadata: "
                f"HTTP Error 404: Not Found (caused by <HTTPError 404: Not Found>)"
            )
            url = f"https://{track['source']}.com/{track['artist'].lower().replace(' ', '-')}/{track['title'].lower().replace(' ', '-')}"
            logger.error(
                f"Error processing URL {url}: "
                f"[{track['source']}] Unable to download JSON metadata: HTTP Error 404: Not Found"
            )
            continue

        if track.get("skip"):
            filename = f"{track['artist']} - {track['title']}.m4a"
            logger.info(f"Already exists, skipping: {_OUTPUT_DIR}/{filename}")
            continue

        _simulate_download(track)

    logger.info("Download complete.")


# ─── Subparser ───────────────────────────────────────────────────────────────

def create_subparser(subparsers):
    parser = subparsers.add_parser(
        "downloadTest",
        help="Simulate download command output without making real requests",
        aliases=["dl-test", "test-dl"],
    )
    parser.set_defaults(func=run_download_test)
