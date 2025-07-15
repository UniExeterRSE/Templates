import base64
import binascii
import os
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image

from config import get_config

config = get_config()
DEFAULT_USER_BASE_FOLDER = Path(config["DEFAULT_USER_BASE_FOLDER"])


def create_user_directory(username: str) -> None:
    """
    Create a folder for the user if it does not exist.

    Parameters
    ----------
    username : str
        Username for which to create the folder.
    """
    try:
        user_folder_path = DEFAULT_USER_BASE_FOLDER / username
        user_folder_path.mkdir(parents=True, exist_ok=True)
    except Exception:
        raise IOError(f"Failed to create user directory for {username}")


def get_user_directory(username: str) -> Path:
    """
    Return the path to the user's directory.

    Parameters
    ----------
    username : str
        Username to get the directory for.

    Returns
    -------
    Path
        Path to the user's directory.
    """
    user_dir = DEFAULT_USER_BASE_FOLDER / username
    if not user_dir.exists():
        raise FileNotFoundError(f"User directory does not exist: {user_dir}")
    return user_dir


def create_timestamped_folder(user_dir: Path, subfolder: str = "mothermachine") -> Path:
    """
    Create a new folder with a timestamp in the user's subdirectory.

    Parameters
    ----------
    user_dir : Path
        User's base directory.
    subfolder : str, optional
        Subdirectory name (default: "mothermachine").

    Returns
    -------
    Path
        Path to the created timestamped folder.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = user_dir / subfolder
    timestamped_dir = target_dir / timestamp
    timestamped_dir.mkdir(parents=True, exist_ok=True)
    return timestamped_dir


def get_image_filenames(dir: Path) -> list[str]:
    """
    Get the path to the user's images directory.

    Parameters
    ----------
    username : str
        Username to get the images directory for.

    Returns
    -------
    Path
        Path to the user's images directory.
    """

    if not os.path.exists(dir):
        raise FileNotFoundError(f"Directory does not exist: {dir}")
    image_files = [
        f
        for f in os.listdir(dir)
        if f.lower().endswith((".tif", ".tiff", ".jpg", ".jpeg", ".png"))
    ]
    return image_files


# --- Image utilities ---
def create_tif_zip_archive(image_arrays: list[np.ndarray]) -> BytesIO:
    """
    Write image arrays as TIFF files to a zip archive in memory.

    Parameters
    ----------
    image_arrays: list of Image
        List of image arrays to write to the zip archive.

    Returns
    -------
    BytesIO
        In-memory zip archive containing TIFF files.
    """
    try:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, mode="w") as zipf:
            for idx, image in enumerate(image_arrays):
                filename = f"{idx}.tif"
                tiff_bytes = get_tiff_bytes(image)
                zipf.writestr(filename, tiff_bytes)
        zip_buffer.seek(0)
        return zip_buffer
    except Exception as e:
        raise IOError(f"Failed to create TIFF zip archive: {str(e)}")


def get_tiff_bytes(array: np.ndarray) -> bytes:
    """
    Convert an image array to TIFF bytes.

    Parameters
    ----------
    array : Image or Mask
        Image or Mask array to convert.

    Returns
    -------
    bytes
        TIFF image bytes.
    """
    try:
        tif_stream = BytesIO()
        image = Image.fromarray(array)
        image.save(tif_stream, format="TIFF")
        data_bytes = tif_stream.getvalue()
        return data_bytes
    except Exception as e:
        raise IOError(f"Failed to convert image array to TIFF image bytes: {str(e)}")


def get_image_arrays_from_folder(folder_path: Path) -> list[np.ndarray]:
    """
    Get a list of Image arrays from TIFF files in a folder.

    Parameters
    ----------
    folder_path : Path
        Path to the folder containing TIFF files.

    Returns
    -------
    list[Image]
        List of Image arrays loaded from the TIFF files.
    """
    images = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".tif"):
            file_path = folder_path / filename
            with Image.open(file_path) as img:
                images.append(np.array(img))
    return images


def write_images_to_folder(folder_path: Path, images: list[np.ndarray]) -> None:
    """
    Save image arrays as TIFF files in a folder.

    Parameters
    ----------
    folder_path : Path
        Folder to save TIFF files in.
    images : list of Image
        Image arrays to write.
    """
    try:
        for image, i in images:
            filename = f"{i}.tif"
            tif_file_path = folder_path / filename
            image = Image.fromarray(image)
            image.save(tif_file_path, format="TIFF")
    except Exception as e:
        raise IOError(f"Failed to write images to folder {folder_path}: {str(e)}")


def validate_image_content(content: bytes) -> None:
    """
    Validate that the provided bytes represent a valid image.

    Parameters
    ----------
    content : bytes
        Image content as bytes.

    Raises
    ------
    ValueError
        If the bytes do not represent a valid image.
    """
    try:
        with Image.open(BytesIO(content)) as img:
            img.verify()
    except (OSError, ValueError) as e:
        raise ValueError(f"Invalid image content: {str(e)}") from e


def decode_base64_image(content_str: str) -> bytes:
    """
    Decode a base64-encoded string to bytes.

    Parameters
    ----------
    content_str : str
        A string containing base64-encoded data, typically in the format "data:<mime>;base64,<encoded_data>".

    Returns
    -------
    bytes
        The decoded bytes from the base64-encoded string.

    Raises
    ------
    ValueError
        If the input string does not contain a comma to split the header and data, or if the decoded content is empty.
    binascii.Error
        If the base64 decoding fails due to invalid input.

    Examples
    --------
    >>> encoded = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
    >>> data = decode_base64_image(encoded)
    """
    try:
        if "," not in content_str:
            raise ValueError(
                "Input string does not contain a comma to split header and data."
            )
        _, split_content_str = content_str.split(",", 1)
        decoded_content_bytes = base64.b64decode(split_content_str)
        if not decoded_content_bytes:
            raise ValueError("Decoded image content is empty.")
        return decoded_content_bytes
    except (ValueError, binascii.Error) as e:
        raise ValueError(f"Failed to decode base64 image: {str(e)}") from e


def save_image_from_bytes(content: bytes, filename: str, upload_dir: Path) -> Path:
    """
    Save an image from bytes to a file in the specified upload directory.

    Parameters
    ----------
    content : bytes
        Image content as bytes.
    filename : str
        Name of the file to save.
    upload_dir : Path
        Directory to save the file in.

    Returns
    -------
    Path
        Path to the saved image file.

    Raises
    ------
    IOError
        If the image cannot be saved or the content is not a valid image.
    """
    try:
        # Ensure the upload directory exists
        upload_dir.mkdir(parents=True, exist_ok=True)
        with Image.open(BytesIO(content)) as image:
            safe_filename = Path(filename).name
            file_path = upload_dir / safe_filename
            image.save(file_path)
            return file_path
    except Exception as e:
        raise IOError(f"Failed to save image '{filename}': {str(e)}") from e
