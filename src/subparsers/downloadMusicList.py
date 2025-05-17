import os
import pandas as pd  # type: ignore
import yt_dlp

# Utils
from src.utils.ytDownloader import download_file
from src.utils.xlsx import append_to_past_downloads
from src.config import get_logger

logger = get_logger(__name__)


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
            df = pd.read_excel(file, sheet_name="music-download-list")
        elif "toDownload" in sheet_names:
            df = pd.read_excel(file, sheet_name="toDownload")
        elif "Found" in sheet_names:
            df = pd.read_excel(file, sheet_name="Found")
        elif "found" in sheet_names:
            df = pd.read_excel(file, sheet_name="found")
        else:
            logger.error("No suitable sheet found in Excel file.")
            return
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        return

    # Check if the DataFrame is empty
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
            # Simulate metadata extraction
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
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

            base_name = f"{artist_name} - {title}.m4a"

            # Check if file already exists
            full_path = os.path.join(output_dir, base_name) if output_dir else base_name
            if os.path.exists(full_path):
                logger.info(f"Already exists, skipping: {full_path}")
                continue

            # Create filename template to output with yt-dlp
            outtmpl = full_path.replace(".m4a", ".%(ext)s")

            # Download the file using yt-dlp
            logger.info(f"Downloading {url} to {outtmpl}")
            download_file(outtmpl, url, metadata={"title": title, "artist": uploader})

            # Append the newly downloaded file to the past downloads sheet
            append_to_past_downloads(file, url, title, uploader)
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")


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
