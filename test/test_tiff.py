import numpy as np

from pathlib import Path
from xtiff import to_tiff


def test_to_tiff(tmp_path: Path):
    path = tmp_path / 'test.ome.tiff'
    num_channels = 10
    img = np.zeros((1, 1, num_channels, 200, 200, 1))
    channel_names = [f'Channel {i + 1}' for i in range(num_channels)]
    to_tiff(img, path, image_name='test.ome.tiff', channel_names=channel_names)
