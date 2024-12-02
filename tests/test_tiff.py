from pathlib import Path

import numpy as np
import tifffile

from xtiff import to_tiff


def test_to_tiff(tmp_path: Path):
    path = tmp_path / "test.ome.tiff"
    num_channels = 10
    x_dim = 15
    y_dim = 20
    img = np.random.randint(
        100, size=(1, 1, num_channels, x_dim, y_dim, 1), dtype=np.uint8
    )
    channel_names = [f"Channel {i + 1}" for i in range(num_channels)]
    to_tiff(
        img,
        path,
        image_name="test.ome.tiff",
        channel_names=channel_names,
        pixel_size=1.0,
        pixel_depth=2.0,
    )
    img_read = tifffile.imread(path)
    # Check if image is read correctly
    assert img_read.shape == (num_channels, x_dim, y_dim)
    assert (img_read == img.squeeze()).all()
