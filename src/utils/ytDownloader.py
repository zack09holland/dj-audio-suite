import subprocess
from yt_dlp.postprocessor import MetadataParserPP
import yt_dlp
from src.config import get_logger

logger = get_logger(__name__)


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
def download_file(outtmpl, url):

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
        "postprocessor_args": [
            "-c:v",
            "mjpeg",
            "-vf",
            "crop='if(gt(ih,iw),iw,ih)':'if(gt(iw,ih),ih,iw)'",
        ],
        "quiet": False,
        "progress_hooks": [lambda d: logger.info(d.get("_percent_str", ""))],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    logger.info(f"Successfully downloaded: {full_path}")
