# Download Music List Script

This script is designed to download music files from URLs specified in an Excel file. It uses the `yt-dlp` library to handle downloading and metadata processing. The script supports downloading audio files, embedding metadata, and saving the files to a specified directory.

## Features
- Reads a list of music download URLs from an Excel file.
- Downloads audio files in the best available quality.
- Embeds metadata and thumbnails into the downloaded files.
- Supports specifying an output directory for saving the files.

## Prerequisites
Before running the script, ensure you have the following installed:
1. Python 3.10 or higher.
2. Required Python libraries:
   - `pandas`
   - `yt-dlp`
   - `openpyxl` (for reading Excel files)

You can install the required libraries using the following command:
```bash
pip install -r requirements.txt
```

# Usage
1. Prepare the Excel File
Create an Excel file with a sheet named music-download-list. The sheet should contain a column named URL with the URLs of the music files you want to download.

2. Run the Script
To run the script, use the following command:
```bash
python run.py downloadMusicList --file <path_to_excel_file> --output <output_directory>
```

## Arguments:
--file (required): Path to the Excel file containing the music download list.
--output (optional): Directory to save the downloaded files. If not specified, the current directory will be used.

### Example:
```zsh
python run.py downloadMusicList --file 'C:\Users\USERNAME\Desktop\music-download-list.xlsx' --output <file_path>
```

If using WSL on windows:
```zsh
python run.py downloadMusicList '/mnt/c/Users/zack09holland/Downloads/music-download-list.xlsx' --output <output_file_path>
```

Recommended to make the python file an executable so you don't need to use `python` in the front of the call.
Better yet, I recommend creating an alias in your .bashrc or .zshrc file to do the work for you so you can run the commands from any directory.
Like so:
```zsh
alias run='python /mnt/c/Users/zack09holland/MyDrive/Programming/python/DJAudioSuite/run.py
```

3. Output
The downloaded audio files will be saved in the specified output directory (or the current directory if no output directory is provided).
Metadata and thumbnails will be embedded into the audio files.

The script logs its progress and any errors encountered during execution. Logs can be viewed in the console or configured to be saved to a file by modifying the logger configuration in src/config.py.

## Development
If you want to add additional commands to run, create a .py file in the subparsers directory and follow
the format of the current subparser files.

Also need to make sure you add the command to the "enabled commands" array in the config.toml file



# License
This project is licensed under the MIT License. See the LICENSE file for details. ```