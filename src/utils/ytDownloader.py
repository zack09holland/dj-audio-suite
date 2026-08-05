import os
import re
import shutil
import subprocess

from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from yt_dlp.postprocessor import MetadataParserPP
import yt_dlp
from src.config import get_logger

# Utils
from src.utils.metadata import clean_keywords

logger = get_logger(__name__)

# Detect the first available JS runtime for yt-dlp YouTube extraction
def _detect_js_runtime():
    for runtime in ("node", "nodejs", "deno"):
        if shutil.which(runtime):
            return runtime
    return None

_JS_RUNTIME = _detect_js_runtime()


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
        # Suppress all [download] lines — destination is logged before the bar starts
        if msg.startswith("[download]"):
            return

    def info(self, msg):
        self._log.info(msg)

    def warning(self, msg):
        self._log.warning(msg)

    def error(self, _msg):
        pass  # errors are caught and reported by the caller's except block


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

    # Maps yt-dlp postprocessor class names to (start%, end%, label)
    _PP_SLOTS = {
        "FixupM4a":           (80.0,  85.0, "Fixing container"),
        "FFmpegExtractAudio": (85.0,  90.0, "Extracting audio"),
        "FFmpegMetadata":     (90.0,  95.0, "Writing metadata"),
        "EmbedThumbnail":     (95.0, 100.0, "Embedding thumbnail"),
    }
    _bitrate = [None]

    progress = Progress(
        TextColumn("  "),
        BarColumn(bar_width=40, complete_style="green", finished_style="green"),
        TaskProgressColumn(),
        TextColumn("[cyan]{task.fields[speed]}[/cyan]"),
        TimeRemainingColumn(),
        TextColumn("[dim]{task.description}[/dim]"),
        transient=False,
        refresh_per_second=10,
    )
    task_id = progress.add_task("Downloading", total=100.0, speed="")

    def _on_progress(d):
        status = d.get("status")
        if status == "downloading":
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
            suffix = f"{speed}  eta {eta}" if speed else ""
            progress.update(task_id, completed=dl_pct * 0.80, speed=suffix, description="Downloading")
        elif status == "finished":
            info = d.get("info_dict", {})
            _bitrate[0] = info.get("abr") or info.get("tbr")
            progress.update(task_id, completed=80.0, speed="", description="Post-processing...")

    def _on_postprocessor(d):
        pp = d.get("postprocessor", "")
        pp_status = d.get("status")
        slot = _PP_SLOTS.get(pp)
        if slot is None:
            return
        start_pct, end_pct, label = slot
        if pp_status == "started":
            progress.update(task_id, completed=start_pct, description=label + "...")
        elif pp_status == "finished":
            progress.update(task_id, completed=end_pct)
            if end_pct >= 100.0:
                progress.update(task_id, description="Done!")

    ydl_opts = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "outtmpl": outtmpl,
        **({"js_runtimes": {_JS_RUNTIME: {}}} if _JS_RUNTIME else {}),
        "remote_components": ["ejs:github"],
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
        "noprogress": True,
        "logger": YtDlpLogger(logger),
        "progress_hooks": [_on_progress],
        "postprocessor_hooks": [_on_postprocessor],
    }

    with progress:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    bitrate_str = f" @ {_bitrate[0]:.0f}kbps" if _bitrate[0] else ""
    name = os.path.basename(outtmpl).replace(".%(ext)s", "")
    logger.info(f"Successfully downloaded: {name}{bitrate_str}")
