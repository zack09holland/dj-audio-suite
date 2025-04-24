import os
import pandas as pd  # type: ignore
import yt_dlp
from yt_dlp.postprocessor import MetadataParserPP

from src.config import get_logger

logger = get_logger(__name__)


# --------------------------------- download_music_from_xlsx ---------------------------------
def download_music_from_xlsx(args):
    logger.info(args)
    file = args.get("file")
    output_dir = args.get("output")  # Can be None

    if not os.path.exists(file):
        logger.error(f"File {file} does not exist")
        return

    try:
        df = pd.read_excel(file, sheet_name="music-download-list")
    except Exception as e:
        logger.error(f"Error reading file {file}: {e}")
        return

    # Create output directory if specified and doesn't exist)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")

    for index, row in df.iterrows():
        try:
            url = row["URL"]
        except KeyError as e:
            logger.error(f"Error reading URL from row {index}: {e}")
            continue

        try:
            # Extract metadata without downloading
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                title = info_dict.get("title", "Unknown Title")
                uploader = info_dict.get("uploader", "Unknown Uploader")

            # Determine filename format
            if "-" in title:
                filename = f"{title}.%(ext)s"
            else:
                filename = f"{uploader} - {title}.%(ext)s"

            # Set output template
            outtmpl = filename
            if output_dir:
                outtmpl = os.path.join(output_dir, filename)

            ydl_opts = {
                "format": "bestaudio/best",
                "extractaudio": True,  # Download only audio
                "outtmpl": outtmpl,  # Output template
                "writethumbnail": True,  # Write thumbnail to file
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "m4a",
                    },  # Use m4a for audio
                    {
                        # Embed metadata into the file
                        "key": "FFmpegMetadata",
                        "add_metadata": True,
                    },
                    {"key": "EmbedThumbnail"},  # Embed thumbnail into the file
                    {
                        "key": "MetadataParser",  # Custom metadata parser
                        "when": "pre_process",
                        "actions": [
                            (
                                MetadataParserPP.Actions.INTERPRET,
                                "%(description,webpage_url).4s",  # Clears the comment field
                                "(?P<meta_comment>)",
                            ),
                            (
                                MetadataParserPP.Actions.INTERPRET,
                                "%(upload_date,release_year).4s",  # Extracts the year from upload date
                                "(?P<meta_date>.+)",
                            ),
                        ],
                    },
                ],
                "postprocessor_args": [
                    "-c:v",  # Set video codec
                    "mjpeg",  # force mjpeg encoding (for jpg thumbnails)
                    "-vf",  # Video filter for cropping
                    "crop='if(gt(ih,iw),iw,ih)':'if(gt(iw,ih),ih,iw)'",  # center crop to square,
                ],
                "quiet": False,  # Show progress
                # "logger": logger,  # Use custom logger
                "progress_hooks": [
                    lambda d: logger.info(d.get("_percent_str", ""))
                ],  # Log download progress
            }

            logger.info(f"Downloading: {url}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            logger.info(f"Successfully downloaded: {filename.replace('%(ext)s', '')}")

        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")


def create_subparser(subparsers):
    command_parser = subparsers.add_parser(
        "downloadMusicList",
        help="Download music from xlsx file",
        aliases=["download", "download-music", "dl"],
    )

    # Required arguments
    command_parser.add_argument(
        "--file", required=True, help="The xlsx file containing music download list"
    )

    # Optional arguments
    command_parser.add_argument(
        "--output",
        default=None,
        help="Directory to save downloaded files (default: current directory)",
    )

    command_parser.set_defaults(func=download_music_from_xlsx)
