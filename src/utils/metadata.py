from mutagen.mp4 import MP4
import unicodedata
import string


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


# --------------------------------- remove_special_characters ---------------------------------
def remove_special_characters(text):
    cleaned = "".join(
        c
        for c in text
        if unicodedata.category(c)[0]
        not in ["C", "S"]  # Remove Other (C) and Symbol (S) categories
    )
    return cleaned.strip()
