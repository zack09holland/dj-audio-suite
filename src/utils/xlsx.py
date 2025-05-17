import pandas as pd  # type: ignore


# --------------------------------- append_to_past_downloads ---------------------------------
def append_to_past_downloads(file, url, title, uploader):
    # Try to load the existing 'pastDownloads' sheet
    try:
        past_df = pd.read_excel(file, sheet_name="pastDownloads")
    except (FileNotFoundError, ValueError):
        # If the file or sheet doesn't exist, start a new DataFrame
        past_df = pd.DataFrame(columns=["URL", "Title", "Uploader"])

    # Create the new row
    new_row = pd.DataFrame([{"URL": url, "Title": title, "Uploader": uploader}])

    # Append and write back
    updated_df = pd.concat([past_df, new_row], ignore_index=True)

    with pd.ExcelWriter(
        file, mode="a", if_sheet_exists="replace", engine="openpyxl"
    ) as writer:
        updated_df.to_excel(writer, sheet_name="pastDownloads", index=False)
