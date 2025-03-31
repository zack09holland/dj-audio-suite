import os
import shutil
import sys

def copyFolder(src_folder, dest_folder):
    try:
        # Check if the source folder exists
        if os.path.exists(src_folder):
            print(f"Moving folder from {src_folder} to {dest_folder}...")
            shutil.move(src_folder, dest_folder)
            print("Folder moved successfully!")
        else:
            print(f"Source folder '{src_folder}' not found. Please ensure the USB drive is connected.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Get the current drive where the script is running from (USB drive)
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    source_folder = os.path.join(script_dir, "_Serato_")  # Folder to move from the USB drive
    destination_folder = r"C:\Music\_Serato_"  # Destination folder on C drive
    print(f"Destination Folder: {destination_folder}")
    copyFolder(source_folder, destination_folder)

if __name__ == "__main__":
    main()
