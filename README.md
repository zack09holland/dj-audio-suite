# DJAudioSuite

A CLI toolkit for DJs and music collectors to download, organize, and manage audio files. Built around `yt-dlp` with a clean terminal UI including colored logs and an in-place progress bar.

---

## Features

- Download audio from SoundCloud, YouTube, and other yt-dlp supported sources
- Embeds metadata (title, artist, year) and album art thumbnails into downloaded files
- Organizes music by genre into folder categories
- Duplicate detection — checks both the local filesystem and the `pastDownloads` Excel sheet before downloading
- Converts audio files to ALAC/M4A format
- Searches your local music library by artist or song name
- Looks up YouTube URLs from an Excel file of artist/title pairs
- Cleans messy title metadata from MP4 files
- Color-coded logs with an animated download progress bar

---

## Prerequisites

- Python 3.10 or higher
- `ffmpeg` installed and available on your PATH (required for audio extraction and thumbnail embedding)

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

All commands are run through `run.py`:

```bash
python run.py <command> [options]
```

**Tip:** Create a shell alias so you can run commands from any directory:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias djas='python /mnt/c/Users/zack09holland/MyDrive/Programming/python/DJAudioSuite/run.py'
```

---

## Commands

### `downloadMusicList`
Aliases: `download`, `download-music`, `dl`

Downloads audio files from URLs listed in an Excel file. Extracts metadata via yt-dlp, embeds it into the file along with the album art thumbnail, and logs the download to the `pastDownloads` sheet.

Skips files that already exist on disk or are already recorded in the `pastDownloads` sheet.

```bash
python run.py downloadMusicList --file <path_to_excel> --output <output_directory>
```

| Argument | Required | Description |
|---|---|---|
| `--file` | Yes | Path to the Excel file containing a `URL` column |
| `--output` | No | Directory to save downloaded files (defaults to current directory) |

**Excel sheet:** The input sheet should be named one of: `music-download-list`, `toDownload`, `Found`, or `found`, with a `URL` column.

**WSL example:**
```bash
python run.py dl --file '/mnt/c/Users/zack09holland/Downloads/music-download-list.xlsx' --output '/mnt/c/Users/zack09holland/Downloads/downloaded'
```

---

### `audioMigration`
Aliases: `migrate`, `audiomigrate`, `am`, `transfer`, `move`

Reads genre metadata from audio files and moves/copies them into genre-based subfolders.

```bash
python run.py audioMigration --source <source_dir> --destinations <dest1> [dest2] --transfer-type <move|copy|both>
```

| Argument | Required | Description |
|---|---|---|
| `--source` | No | Source directory (defaults to `refined-audio/`) |
| `--destinations` | No | One or more destination directories |
| `--transfer-type` | Yes | `move`, `copy`, or `both` |

Supported formats: `.mp3`, `.m4a`, `.flac`, `.wav`, `.opus`

---

### `localMusicSearch`
Aliases: none

Searches your local music library for files matching an artist or song name.

```bash
python run.py localMusicSearch --search_term <query> --music_dir <directory>
```

---

### `convertToALAC`
Aliases: none

Converts `.opus`, `.wav`, or `.flac` files to ALAC (`.m4a`) using ffmpeg.

```bash
python run.py convertToALAC --input <file_or_directory> --output_folder <output_directory>
```

---

### `getYouTubeUrls`
Aliases: none

Reads an Excel file with `Artist` and `Title` columns and writes the best matching YouTube URL for each row into a new column.

```bash
python run.py getYouTubeUrls --file <path_to_excel>
```

Output is saved as `<original_filename>_with_urls.xlsx`.

---

### `getSongInfo`
Aliases: none

Reads the `pastDownloads` sheet and fetches additional metadata (title, uploader) for each entry via yt-dlp.

```bash
python run.py getSongInfo --file <path_to_excel>
```

---

### `cleanMetadata`
Aliases: none

Removes the artist prefix from an MP4 file's title tag (everything before the first ` - `).

```bash
python run.py cleanMetadata --file <path_to_m4a>
```

---

### `search_1001tracklists`
> **Work in progress** — not yet functional.

---

### `downloadTest`
Aliases: `dl-test`, `test-dl`

Runs a simulated download with fake tracks to preview the terminal output and progress bar without making any real network requests.

```bash
python run.py downloadTest
```

---

### `audioMigrationTest`
Aliases: `am-test`, `test-am`

Runs a simulated audio migration across fake tracks and genres to preview the terminal output without touching real files.

```bash
python run.py audioMigrationTest
```

---

## pastDownloads Sheet

Each successful download appends a row to the `pastDownloads` sheet in your Excel file:

| Column | Description |
|---|---|
| `Date Downloaded` | Date the file was downloaded (`MM/DD/YYYY`) |
| `URL` | Source URL |
| `Title` | Track title |
| `Uploader` | Artist / uploader name |

---

## Adding New Commands

1. Create a new `.py` file in `src/subparsers/`
2. Implement your logic and a `create_subparser(subparsers)` function following the pattern of existing subparsers
3. Add the module name to `enabled_commands` in `config.toml`

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
