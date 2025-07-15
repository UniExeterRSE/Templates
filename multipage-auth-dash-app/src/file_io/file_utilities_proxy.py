"""
Proxy module for file utilities (folder and image operations).
Allows for easy mocking, extension, or swapping of file utility logic in tests or other environments.
"""

from io import BytesIO
from pathlib import Path

import numpy as np

from . import file_utilities


def decode_base64_image(content: str) -> bytes:
    return file_utilities.decode_base64_image(content)


def create_user_directory(username: str) -> None:
    return file_utilities.create_user_directory(username)


def get_user_directory(username: str) -> Path:
    return file_utilities.get_user_directory(username)


def get_image_filenames(dir: Path) -> list[str]:
    return file_utilities.get_image_filenames(dir)


def create_tif_zip_archive(image_arrays: list[np.ndarray]) -> BytesIO:
    return file_utilities.create_tif_zip_archive(image_arrays)


def get_tiff_bytes(array: np.ndarray) -> bytes:
    return file_utilities.get_tiff_bytes(array)


def write_images_to_folder(folder_path: Path, image_arrays: list[np.ndarray]) -> None:
    return file_utilities.write_images_to_folder(folder_path, image_arrays)


def validate_image_content(content: bytes) -> None:
    return file_utilities.validate_image_content(content)


def save_image_from_bytes(content: bytes, filename: str, upload_dir: Path) -> Path:
    return file_utilities.save_image_from_bytes(content, filename, upload_dir)


def get_image_arrays_from_folder(folder_path: Path) -> list[np.ndarray]:
    return file_utilities.get_image_arrays_from_folder(folder_path)
