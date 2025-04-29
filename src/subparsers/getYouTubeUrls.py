import pandas as pd

# Utils
from src.utils.ytDownloader import search_youtube_url

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
    if "URL" not in df.columns:
        df["URL"] = ""

    found_rows = []
    not_found_rows = []

    # Loop through each row
    for idx, row in df.iterrows():
        artist = row.get("ZARTISTNAME") or row.get("artist") or row.get("Artist")
        title = row.get("ZTITLE") or row.get("title") or row.get("Title")

        if pd.notna(artist) and pd.notna(title):
            logger.info(f"Searching for: {artist} - {title}")
            url = search_youtube_url(artist, title)
            if url:
                row["URL"] = url
                found_rows.append(row)
            else:
                not_found_rows.append(row)

    # Create DataFrames
    found_df = pd.DataFrame(found_rows)
    not_found_df = pd.DataFrame(not_found_rows)

    # Save both DataFrames into one Excel file with two sheets
    with pd.ExcelWriter(output_file) as writer:
        found_df.to_excel(writer, sheet_name="Found", index=False)
        not_found_df.to_excel(writer, sheet_name="Not found", index=False)

    logger.info(
        f"Done! {len(found_df)} songs found, {len(not_found_df)} not found. Results saved to {output_file}"
    )


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
