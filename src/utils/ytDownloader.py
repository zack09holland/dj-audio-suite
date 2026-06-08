import re
import sys
import subprocess

from colorama import Fore, Style
from yt_dlp.postprocessor import MetadataParserPP
import yt_dlp
from src.config import get_logger

# Utils
from src.utils.metadata import clean_keywords

logger = get_logger(__name__)


# --------------------------------- YtDlpLogger ---------------------------------
# Filters yt-dlp's internal verbose messages and routes useful steps through
# our logger so the terminal output is clean and readable.
class YtDlpLogger:
    # Internal messages to suppress entirely
    _SUPPRESS_PREFIXES = (
        "[MetadataParser]",
        "[hlsnative]",
        "[info] Downloading video thumbnail",
        "[info] Writing video thumbnail",
        "[debug] ",
    )
    # Regex for per-source "Downloading X info JSON" chatter
    _SUPPRESS_RE = re.compile(
        r"^\[.*?\] .*?: Downloading (info JSON|(hls|http)_\w+ format info JSON)$"
        r"|^\[.*?\] Extracting URL:"
        r"|^\[.*?\] .*?: Downloading \d+ format"
        r"|^\[info\] \d+: Downloading"
    )
    def __init__(self, app_logger):
        self._log = app_logger

    def debug(self, msg):
        if any(msg.startswith(p) for p in self._SUPPRESS_PREFIXES):
            return
        if self._SUPPRESS_RE.match(msg):
            return
        # Show destination file path (prints before the progress bar starts)
        if "[download] Destination:" in msg:
            dest = msg.split("Destination:", 1)[1].strip()
            self._log.info(f"  -> Saving to: {dest}")
            return
        # Suppress all [download] fragment/progress lines — the bar handles these
        if msg.startswith("[download]"):
            return

    def info(self, msg):
        self._log.info(msg)

    def warning(self, msg):
        self._log.warning(msg)

    def error(self, msg):
        self._log.error(msg)


# --------------------------------- search_youtube_url ---------------------------------
# Function to search and get YouTube URL
def search_youtube_url(artist, title):
    query = f"ytsearch1:{artist} - {title}"
    try:
        result = subprocess.run(
            ["yt-dlp", query, "--skip-download", "--print", "%(webpage_url)s"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        url = result.stdout.strip()
        return url if url.startswith("http") else None
    except Exception as e:
        logger.error(f"Error fetching URL for {artist} - {title}: {e}")
        return None


# --------------------------------- downloadFile ---------------------------------
def download_file(outtmpl, url, metadata=None):
    post_args = [
        "-c:v",
        "mjpeg",
        "-vf",
        "crop='if(gt(ih,iw),iw,ih)':'if(gt(iw,ih),ih,iw)'",
    ]

    # Add metadata override arguments
    if metadata:
        if metadata.get("title"):
            cleaned_title = clean_keywords(metadata["title"])
            post_args += ["-metadata", f"title={cleaned_title}"]
        if metadata.get("artist"):
            cleaned_artist = clean_keywords(metadata["artist"])
            post_args += ["-metadata", f"artist={cleaned_artist}"]

    # Unified progress bar covering download (0-80%) + post-processing (80-100%)
    _BAR_WIDTH = 40
    # Maps yt-dlp postprocessor class names to (start%, end%, label)
    _PP_SLOTS = {
        "FixupM4a":           (80.0,  85.0, "Fixing container"),
        "FFmpegExtractAudio": (85.0,  90.0, "Extracting audio"),
        "FFmpegMetadata":     (90.0,  95.0, "Writing metadata"),
        "EmbedThumbnail":     (95.0, 100.0, "Embedding thumbnail"),
    }
    # Guard: once we've printed the final 100% bar, ignore all further hook calls
    _bar_done = [False]

    def _draw(pct: float, suffix: str = ""):
        if _bar_done[0]:
            return
        filled = int(_BAR_WIDTH * pct / 100)
        bar = (
            Fore.GREEN + "█" * filled
            + Style.DIM + "░" * (_BAR_WIDTH - filled)
            + Style.RESET_ALL
        )
        line = f"\r  [{bar}] {Fore.CYAN}{pct:5.1f}%{Style.RESET_ALL}"
        if suffix:
            line += f"  {suffix}"
        # Pad to overwrite any leftover chars from a longer previous line
        sys.stdout.write(line.ljust(120))
        sys.stdout.flush()

    def _on_progress(d):
        status = d.get("status")
        if status == "downloading":
            # HLS streams report per-fragment; use fragment counts when available
            frag_idx = d.get("fragment_index")
            frag_cnt = d.get("fragment_count")
            if frag_idx is not None and frag_cnt:
                dl_pct = frag_idx / frag_cnt * 100
            else:
                try:
                    dl_pct = float(d.get("_percent_str", "0%").strip().rstrip("%"))
                except (ValueError, AttributeError):
                    return
            speed = d.get("_speed_str", "").strip()
            eta = d.get("_eta_str", "").strip()
            # Download phase occupies 0-80% of the bar
            _draw(dl_pct * 0.80, f"{speed}  eta {eta}")
        elif status == "finished":
            _draw(80.0, "Post-processing...")

    def _on_postprocessor(d):
        pp = d.get("postprocessor", "")
        status = d.get("status")
        slot = _PP_SLOTS.get(pp)
        if slot is None:
            return
        start_pct, end_pct, label = slot
        if status == "started":
            _draw(start_pct, f"{label}...")
        elif status == "finished":
            if end_pct >= 100.0:
                _bar_done[0] = True
                filled = "█" * _BAR_WIDTH
                sys.stdout.write(
                    f"\r  [{Fore.GREEN}{filled}{Style.RESET_ALL}]"
                    f" {Fore.GREEN}100.0%{Style.RESET_ALL}  Done!".ljust(120) + "\n"
                )
                sys.stdout.flush()
            else:
                _draw(end_pct)

    ydl_opts = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "outtmpl": outtmpl,
        "writethumbnail": True,
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "m4a"},
            {"key": "FFmpegMetadata", "add_metadata": True},
            {"key": "EmbedThumbnail"},
            {
                "key": "MetadataParser",
                "when": "pre_process",
                "actions": [
                    (
                        MetadataParserPP.Actions.INTERPRET,
                        "%(description,webpage_url).4s",
                        "(?P<meta_comment>)",
                    ),
                    (
                        MetadataParserPP.Actions.INTERPRET,
                        "%(upload_date,release_year).4s",
                        "(?P<meta_date>.+)",
                    ),
                ],
            },
        ],
        "postprocessor_args": post_args,
        "quiet": True,
        "logger": YtDlpLogger(logger),
        "progress_hooks": [_on_progress],
        "postprocessor_hooks": [_on_postprocessor],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    logger.info(f"Successfully downloaded: {outtmpl}")
