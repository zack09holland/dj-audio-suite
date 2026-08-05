import os
import re
import pandas as pd  # type: ignore
import yt_dlp

# Utils
from src.utils.ytDownloader import download_file, YtDlpLogger, _JS_RUNTIME
from src.utils.xlsx import (
    append_to_past_downloads,
    append_to_failed_downloads,
    deduplicate_failed_downloads,
    is_already_downloaded,
    mark_url_red,
)
from src.utils.metadata import clean_keywords

from src.config import get_logger

logger = get_logger(__name__)

_SOURCE_MAP = {
    "soundcloud.com": "SoundCloud",
    "youtube.com": "YouTube",
    "youtu.be": "YouTube",
    "spotify.com": "Spotify",
    "tidal.com": "Tidal",
    "deezer.com": "Deezer",
    "bandcamp.com": "Bandcamp",
    "mixcloud.com": "Mixcloud",
    "vimeo.com": "Vimeo",
}

def _parse_source(url: str) -> str:
    match = re.search(r"https?://(?:www\.)?([^/]+)", url)
    if not match:
        return "Unknown"
    domain = match.group(1).lower()
    for key, label in _SOURCE_MAP.items():
        if key in domain:
            return label
    # Fall back to the bare domain name, capitalized
    return domain.split(".")[0].capitalize()


# --------------------------------------- download_music_from_xlsx ---------------------------------------
# - Download music files from an Excel file containing URLs
def download_music_from_xlsx(args):
    logger.info(args)
    file = args.get("file")
    output_dir = args.get("output")  # Can be None

    if not os.path.exists(file):
        logger.error(f"File {file} does not exist")
        return

    # Load all sheet names
    xls = pd.ExcelFile(file)
    sheet_names = xls.sheet_names

    try:
        # Try loading from available sheets
        if "music-download-list" in sheet_names:
            source_sheet = "music-download-list"
        elif "toDownload" in sheet_names:
            source_sheet = "toDownload"
        elif "Found" in sheet_names:
            source_sheet = "Found"
        elif "found" in sheet_names:
            source_sheet = "found"
        else:
            logger.error("No suitable sheet found in Excel file.")
            return
        df = pd.read_excel(file, sheet_name=source_sheet)
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        return

    # Create output directory if it doesn't exist
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")

    for index, row in df.iterrows():
        try:
            url = row["URL"]
        except KeyError as e:
            logger.error(f"Missing 'URL' column at row {index}: {e}")
            continue

        try:
            name = url  # fallback if metadata extraction fails
            source = _parse_source(url)

            # Simulate metadata extraction to get title and artist
            # using yt-dlp to extract metadata without downloading
            with yt_dlp.YoutubeDL(
                {"quiet": True, "logger": YtDlpLogger(logger), "remote_components": ["ejs:github"], **({"js_runtimes": {_JS_RUNTIME: {}}} if _JS_RUNTIME else {})}
            ) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                title_raw = (
                    info_dict.get("title", "Unknown Title").strip().replace("/", "-")
                )
                title = (
                    title_raw.split("-", 1)[-1].strip()
                    if "-" in title_raw
                    else title_raw
                )

                uploader = (
                    info_dict.get("uploader", "Unknown Uploader")
                    .strip()
                    .replace("/", "-")
                )

                # Use semantic metadata if available
                track = info_dict.get("track")
                artist = info_dict.get("artist")
                if "-" in title_raw:
                    parts = title_raw.split("-", 1)
                    artist_name = parts[0].strip().replace("/", "-")
                    title = parts[1].strip().replace("/", "-")
                elif track and artist:
                    title = track.strip().replace("/", "-")
                    artist_name = artist.strip().replace("/", "-")
                else:
                    title = title_raw
                    artist_name = uploader

            # Clean up both artist and title using the shared keyword cleaner
            cleaned_title = clean_keywords(title)
            cleaned_artist_name = clean_keywords(artist_name)

            # Set the base name for the file
            base_name = f"{cleaned_artist_name} - {cleaned_title}.m4a"

            # Check if file already exists on disk
            full_path = os.path.join(output_dir, base_name) if output_dir else base_name
            if os.path.exists(full_path):
                logger.info(f"Already exists, skipping: {full_path}")
                continue

            # Check if already logged in pastDownloads sheet
            if is_already_downloaded(file, cleaned_title, cleaned_artist_name):
                logger.info(
                    f"Already exists, skipping: {cleaned_artist_name} - {cleaned_title}"
                )
                continue

            # Create filename template to output with yt-dlp
            outtmpl = full_path.replace(".m4a", ".%(ext)s")

            # Download the file using yt-dlp
            name = os.path.basename(outtmpl).replace(".%(ext)s", "")
            source = _parse_source(url)
            logger.info(f"Downloading > {name} | {source}")
            logger.info(f"Saving to > {full_path}")
            download_file(
                outtmpl,
                url,
                metadata={"title": cleaned_title, "artist": cleaned_artist_name},
            )

            # Append the newly downloaded file to the past downloads sheet
            append_to_past_downloads(file, url, title, artist_name)
        except Exception as e:
            reason = str(e).removeprefix("ERROR: ").strip()
            logger.error(f"Error [{source}] {name}: {reason}")
            append_to_failed_downloads(file, url, reason)
            mark_url_red(file, url, source_sheet)

    deduplicate_failed_downloads(file)


# --------------------------------------- create_subparser ---------------------------------------
def create_subparser(subparsers):
    command_parser = subparsers.add_parser(
        "downloadMusicList",
        help="Download music from xlsx file",
        aliases=["download", "download-music", "dl"],
    )
    command_parser.add_argument(
        "--file", required=True, help="The xlsx file containing music download list"
    )
    command_parser.add_argument(
        "--output", default=None, help="Directory to save downloaded files"
    )
    command_parser.set_defaults(func=download_music_from_xlsx)
