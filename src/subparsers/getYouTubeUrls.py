import pandas as pd
import subprocess

from src.config import get_logger

logger = get_logger(__name__)


# --------------------------------------- get_youtube_urls ---------------------------------------
# - Get YouTube URLs from an Excel file containing song data (ie. artist and title)
def get_youtube_urls(args):
    input_file = args.get("file")
    output_file = input_file.replace(".xlsx", "_with_urls.xlsx")

    # Load the Excel file
    df = pd.read_excel(input_file)

    # Add a new column for YouTube URLs if it doesn't exist
    if "YOUTUBE_URL" not in df.columns:
        df["YOUTUBE_URL"] = ""

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

    # Loop through each row
    for idx, row in df.iterrows():
        artist = row.get("ZARTISTNAME", "")
        title = row.get("ZTITLE", "")
        if pd.notna(artist) and pd.notna(title):
            logger.info(f"Searching for: {artist} - {title}")
            url = search_youtube_url(artist, title)
            df.at[idx, "YOUTUBE_URL"] = url

    # Save the new file
    df.to_excel(output_file, index=False)
    logger.info(f"Done! Results saved to {output_file}")


# --------------------------------------- create_subparser ---------------------------------------
# - Create a subparser for the getYouTubeUrls command
def create_subparser(subparsers):
    command_parser = subparsers.add_parser(
        "getYouTubeUrls",
        help="Search songs from an Excel file and fetch YouTube URLs",
        aliases=["getUrls", "geturls"],
    )

    # Required argument
    command_parser.add_argument(
        "--file",
        "-s",
        required=True,
        help="Path to the input Excel file containing song data (ZARTISTNAME and ZTITLE columns are required)",
    )

    # Optional argument for music directory (not used here, but kept for compatibility)
    command_parser.add_argument(
        "--music-dir",
        "-d",
        default=".",
        help="Base directory to search from (default: current directory)",
    )

    command_parser.set_defaults(func=get_youtube_urls)
