import os
import subprocess
from src.config import get_logger

logger = get_logger(__name__)

# Supported file extensions to convert
SUPPORTED_EXTENSIONS = (".opus", ".wav", ".flac")


def convert_to_alac(args):
    """Convert audio files to ALAC format (M4A)"""
    input_path = args.get("input")
    output_folder = args.get("output_folder")

    if not os.path.exists(input_path):
        logger.error(f"Input path {input_path} does not exist")
        return

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logger.info(f"Created output directory: {output_folder}")

    if os.path.isfile(input_path):
        _process_file(input_path, output_folder)
    elif os.path.isdir(input_path):
        _process_folder(input_path, output_folder)
    else:
        logger.error(
            f"Invalid input path: {input_path}. Please provide a valid file or folder."
        )


def _process_folder(input_folder, output_folder):
    """Walk through folder and convert supported files"""
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(SUPPORTED_EXTENSIONS):
                input_file = os.path.join(root, file)
                output_file = os.path.join(
                    output_folder, os.path.splitext(file)[0] + ".m4a"
                )
                _convert_file(input_file, output_file)


def _process_file(input_file, output_folder):
    """Process individual file conversion"""
    if input_file.lower().endswith(SUPPORTED_EXTENSIONS):
        output_file = os.path.join(
            output_folder, os.path.splitext(os.path.basename(input_file))[0] + ".m4a"
        )
        _convert_file(input_file, output_file)
    else:
        logger.error(f"Unsupported file format: {input_file}")


def _convert_file(input_file, output_file):
    """Convert single file to ALAC format using ffmpeg"""
    if os.path.exists(output_file):
        logger.info(f"File {output_file} already exists. Skipping conversion.")
        return

    try:
        # ffmpeg command for converting to M4A (ALAC)
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_file,
                "-map_metadata",
                "0",  # Transfer metadata
                "-c:a",
                "alac",  # Use ALAC codec
                "-c:v",
                "copy",  # Copy album art if available
                "-vn",
                "-movflags",
                "+faststart",
                output_file,
            ],
            check=True,
        )
        logger.info(f"Successfully converted: {input_file} -> {output_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error converting {input_file}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing {input_file}: {e}")


def create_subparser(subparsers):
    command_parser = subparsers.add_parser(
        "convertToALAC",
        help="Convert audio files to ALAC format (M4A)",
        aliases=["convert", "alac", "to-alac"],
    )

    # Required arguments
    command_parser.add_argument(
        "--input", required=True, help="Path to the folder or file to convert"
    )

    command_parser.add_argument(
        "--output-folder",
        required=True,
        help="Path to the folder where converted files will be saved",
    )

    command_parser.set_defaults(func=convert_to_alac)
