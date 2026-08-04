import datetime

import pandas as pd  # type: ignore


# --------------------------------- append_to_failed_downloads ---------------------------------
def append_to_failed_downloads(file, url, reason):
    try:
        failed_df = pd.read_excel(file, sheet_name="failedDownloads")
    except (FileNotFoundError, ValueError):
        failed_df = pd.DataFrame(columns=["Date", "URL", "Reason"])

    new_row = pd.DataFrame([{
        "Date": datetime.date.today().strftime("%m/%d/%Y"),
        "URL": url,
        "Reason": str(reason),
    }])

    updated_df = pd.concat([failed_df, new_row], ignore_index=True)

    with pd.ExcelWriter(
        file, mode="a", if_sheet_exists="replace", engine="openpyxl"
    ) as writer:
        updated_df.to_excel(writer, sheet_name="failedDownloads", index=False)


# --------------------------------- is_already_downloaded ---------------------------------
def is_already_downloaded(file, title, uploader):
    try:
        past_df = pd.read_excel(file, sheet_name="pastDownloads")
    except (FileNotFoundError, ValueError):
        return False

    if "Title" not in past_df.columns or "Uploader" not in past_df.columns:
        return False

    match = past_df[
        (past_df["Title"].str.strip().str.lower() == title.strip().lower()) &
        (past_df["Uploader"].str.strip().str.lower() == uploader.strip().lower())
    ]
    return not match.empty


# --------------------------------- append_to_past_downloads ---------------------------------
def append_to_past_downloads(file, url, title, uploader):
    # Try to load the existing 'pastDownloads' sheet
    try:
        past_df = pd.read_excel(file, sheet_name="pastDownloads")
    except (FileNotFoundError, ValueError):
        # If the file or sheet doesn't exist, start a new DataFrame
        past_df = pd.DataFrame(columns=["Date Downloaded", "URL", "Title", "Uploader"])

    # Create the new row
    new_row = pd.DataFrame([{
        "Date Downloaded": datetime.date.today().strftime("%m/%d/%Y"),
        "URL": url,
        "Title": title,
        "Uploader": uploader,
    }])

    # Append and write back
    updated_df = pd.concat([past_df, new_row], ignore_index=True)

    with pd.ExcelWriter(
        file, mode="a", if_sheet_exists="replace", engine="openpyxl"
    ) as writer:
        updated_df.to_excel(writer, sheet_name="pastDownloads", index=False)
