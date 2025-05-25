from mutagen.mp4 import MP4
import unicodedata
import string
import re


# --------------------------------- clean_title_metadata ---------------------------------
def clean_title_metadata(file_path):
    try:
        video = MP4(file_path)

        # Get the current title
        current_title = video.tags.get("\xa9nam", [""])[0]

        # Only update if the title has ' - ' in it
        if " - " in current_title:
            new_title = current_title.split(" - ", 1)[1]
            video.tags["\xa9nam"] = [new_title]
            video.save()
            print(f"Title updated to: {new_title}")
        elif " – " in current_title:
            new_title = current_title.split(" – ", 1)[1]
            video.tags["\xa9nam"] = [new_title]
            video.save()
            print(f"Title updated to: {new_title}")
        else:
            print("No ' - ' found in title, nothing updated.")
    except Exception as e:
        print(f"Error: {e}")


# --------------------------------- clean_keywords ---------------------------------
REMOVE_KEYWORDS = ["OUT NOW", "FREE DOWNLOAD"]


def clean_keywords(text, keywords=REMOVE_KEYWORDS):
    for keyword in keywords:
        # Remove 1 character before and 1 character after the keyword (if present)
        pattern = rf".?{re.escape(keyword)}.?"
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text.strip()


# --------------------------------- remove_special_characters ---------------------------------
def remove_special_characters(text):
    cleaned = "".join(
        c
        for c in text
        if unicodedata.category(c)[0]
        not in ["C", "S"]  # Remove Other (C) and Symbol (S) categories
    )
    return cleaned.strip()
