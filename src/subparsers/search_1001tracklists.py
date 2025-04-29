import pandas as pd
import subprocess
import requests
from bs4 import BeautifulSoup

from src.config import get_logger

logger = get_logger(__name__)

# ------------------------------------------------------------------------------
# This file is part of the 1001tracklists Downloader project
#
# NOTE: It is a WORK IN PROGRESS and is not yet complete.
#
# The Idea:
# - Search 1001tracklists for a given query and return a list of matching tracks
# ------------------------------------------------------------------------------


# --------------------------------------- search_1001tracklists ---------------------------------------
def search_1001tracklists(args):
    query = args.get("query")

    if not query:
        logger.error("No query provided for search_1001tracklists.")
        return []

    logger.info(f"Searching 1001tracklists for query: {query}")

    search_url = "https://www.1001tracklists.com/search/result.php"
    data = {"main_search": query}
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.post(search_url, data=data, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch search results: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    with open("search_results.txt", "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    print(soup.prettify())  # For debugging purposes, can be removed later

    results = []
    for item in soup.select(".content .defaulttrack span.trackTitle a"):
        title = item.text.strip()
        link = "https://www.1001tracklists.com" + item.get("href")
        results.append({"title": title, "url": link})

    logger.info(f"Found {len(results)} results for query: {query}")
    return results


# --------------------------------------- create_subparser ---------------------------------------
def create_subparser(subparsers):
    command_parser = subparsers.add_parser(
        "tracklistApi",
        help="Enables easy access to the 1001tracklists database",
        aliases=["track", "tracklist", "tracklistapi", "tlapi", "tl"],
    )

    command_parser.add_argument(
        "--query",
        "-q",
        required=True,
        help="Search query to look up on 1001tracklists (e.g., artist or track name)",
    )

    command_parser.set_defaults(func=search_1001tracklists)
