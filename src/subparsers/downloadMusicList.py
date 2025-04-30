import os
import pandas as pd  # type: ignore
import yt_dlp

# Utils
from src.utils.ytDownloader import download_file

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

    # Check if the DataFrame has the 'URL' column
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
                title = (
                    info_dict.get("title", "Unknown Title").strip().replace("/", "-")
                )
                uploader = (
                    info_dict.get("uploader", "Unknown Uploader")
                    .strip()
                    .replace("/", "-")
                )

            # Build filename like "artist - title.m4a"
            if "-" in title:
                base_name = f"{title}.m4a"
            else:
                base_name = f"{uploader} - {title}.m4a"

            # Check if file already exists
            full_path = os.path.join(output_dir, base_name) if output_dir else base_name
            if os.path.exists(full_path):
                logger.info(f"Already exists, skipping: {full_path}")
                continue

            # Create filename template to output with yt-dlp
            outtmpl = full_path.replace(".m4a", ".%(ext)s")

            logger.info(f"Downloading {url} to {outtmpl}")

            download_file(outtmpl, url)

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
