import zipfile
from io import BytesIO

import numpy as np
import pytest
from PIL import Image

from file_io.file_utilities import create_tif_zip_archive


@pytest.fixture
def sample_arrays_to_zip():
    """Fixture for creating sample segmentation results."""
    return [
        np.array([[1, 2, 3]], dtype=np.uint8),
        np.array([[4, 5, 6]], dtype=np.uint16),
    ]


def test_write_zip_archive(sample_arrays_to_zip):
    """Test creating a zip archive from segmentation results."""
    zip_buffer = create_tif_zip_archive(sample_arrays_to_zip)

    zip_buffer.seek(0)

    image_arrays = []
    with zipfile.ZipFile(zip_buffer, "r") as zipf:
        # Sort filenames to ensure consistent order for comparison
        filenames = sorted(zipf.namelist())
        for file_name in filenames:
            with zipf.open(file_name) as file:
                with BytesIO(file.read()) as file_bytes:
                    image = Image.open(file_bytes)
                    image_array = np.array(image)
                    image_arrays.append(image_array)

    # Compare the arrays extracted from the zip to the original arrays
    assert len(image_arrays) == len(sample_arrays_to_zip)
    for extracted, original in zip(image_arrays, sample_arrays_to_zip):
        assert np.array_equal(extracted, original)


def test_write_zip_archive_empty_list():
    """Test creating a zip archive with an empty list."""
    zip_buffer = create_tif_zip_archive([])

    zip_buffer.seek(0)

    with zipfile.ZipFile(zip_buffer, "r") as zipf:
        assert len(zipf.namelist()) == 0


@pytest.mark.parametrize("num_files", [1, 3, 5, 10])
def test_write_zip_archive_multiple_files(num_files):
    """Test creating zip archives with different numbers of files."""
    results = [np.array([[i, i + 1, i + 2]], dtype=np.uint8) for i in range(num_files)]

    zip_buffer = create_tif_zip_archive(results)
    zip_buffer.seek(0)

    with zipfile.ZipFile(zip_buffer, "r") as zipf:
        assert len(zipf.namelist()) == num_files
        for i, filename in enumerate(sorted(zipf.namelist())):
            assert filename == f"{i}.tif"
