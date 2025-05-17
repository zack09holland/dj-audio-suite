import pandas as pd
import yt_dlp

# Utils
from src.config import get_logger

logger = get_logger(__name__)


# --------------------------------------- get_song_info ---------------------------------------
# - Get YouTube URLs from an Excel file containing song data (ie. artist and title)
def get_song_info(args):
    input_file = args.get("file")
    output_file = input_file.replace(".xlsx", "_with_urls.xlsx")

    try:
        # Read the "pastDownloads" sheet
        df = pd.read_excel(input_file, sheet_name="pastDownloads")
    except Exception as e:
        logger.error(f"Error reading Excel file or sheet: {e}")
        return

    # Add columns to hold metadata
    df["Uploader"] = ""
    df["Title"] = ""

    for index, row in df.iterrows():
        try:
            url = row["URL"]
        except KeyError as e:
            logger.error(f"Missing 'URL' column at row {index}: {e}")
            continue

        # Skip if URL is empty, NaN, or placeholder
        if not isinstance(url, str) or url.strip() == "" or url.strip() == "---":
            logger.info(f"Skipping invalid or placeholder URL at row {index}")
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

                # Update the DataFrame with the extracted metadata
                df.at[index, "Uploader"] = uploader
                df.at[index, "Title"] = title

                logger.info(f"Processed row {index}: {title} by {uploader}")

        except Exception as e:
            logger.error(f"Error processing URL at row {index}: {url} — {e}")

    try:
        # Save the updated DataFrame
        with pd.ExcelWriter(
            input_file, mode="a", if_sheet_exists="replace", engine="openpyxl"
        ) as writer:
            df.to_excel(writer, sheet_name="pastDownloadss", index=False)

        logger.info(f"Updated file saved as: {input_file}")
    except Exception as e:
        logger.error(f"Error writing Excel file: {e}")


# --------------------------------------- create_subparser ---------------------------------------
# - Create a subparser for the getYouTubeUrls command
def create_subparser(subparsers):
    command_parser = subparsers.add_parser(
        "getSongInfo",
        help="Get the metadata (title and uploader) from a URL and output them into columns of an Excel file",
        aliases=["getInfo", "getinfo", "getSongInfo", "getSonginfo"],
    )

    # Required argument
    command_parser.add_argument(
        "--file",
        "-s",
        required=True,
        help="Path to the input Excel file containing song data (URL column is required)",
    )

    command_parser.set_defaults(func=get_song_info)
