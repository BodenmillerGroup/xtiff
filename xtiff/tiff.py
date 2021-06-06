import numpy as np
import sys
import tifffile
import warnings

from datetime import datetime
from enum import Enum
from io import BytesIO
from pathlib import Path
from tifffile import TiffWriter
from typing import Any, Optional, Sequence, Union

from xtiff.ome import get_ome_xml

try:
    import xarray as xr
except ImportError:
    xr = None


class TiffProfile(Enum):
    TIFF = 1
    IMAGEJ = 2
    OME_TIFF = 3


def to_tiff(img, file, image_name: Union[str, bool, None] = None, image_date: Union[str, datetime, None] = None,
            channel_names: Union[Sequence[str], bool, None] = None, description: Optional[str] = None,
            profile: TiffProfile = TiffProfile.OME_TIFF, big_endian: Optional[bool] = None,
            big_tiff: Optional[bool] = None, big_tiff_threshold: int = 2 ** 32 - 2 ** 25, interleaved: bool = True,
            compression_type: Optional[str] = None, compression_level: int = 0,
            pixel_size: Optional[float] = None, pixel_depth: Optional[float] = None,
            software: str = 'xtiff', ome_xml_fun=get_ome_xml, **ome_xml_kwargs) -> None:
    """
    Writes an image as TIFF file with TZCYX channel order.

    :param img: The image to write, as xarray DataArray or numpy-compatible data structure.
        Supported shapes:
        - (y, x),
        - (c, y, x)
        - (z, c, y, x)
        - (t, z, c, y, x)
        - (t, z, c, y, x, s)
        Supported data types:
        - any numpy data type when using TiffProfile.TIFF
        - uint8, uint16, float32 when using TiffProfile.IMAGEJ (uint8 for RGB images)
        - bool, int8, int16, int32, uint8, uint16, uint32, float32, float64 when using TiffProfile.OME_TIFF
    :param file: File target supported by tifffile TiffWriter, e.g. path to file (str, pathlib.Path) or binary stream.
    :param image_name: Image name for OME-TIFF images. If True, the image name is determined using the DataArray name or
        the file name (in that order); if False, the image name is not set. If None, defaults to the behavior for True
        for named DataArrays and when the file path is provided, and to the behavior of False otherwise. Only relevant
        when writing OME-TIFF files, any value other than None or False will raise a warning for other TIFF profiles.
    :param image_date: Date and time of image creation in '%Y:%m:%d %H:%M:%S' format or as datetime object. Defaults to
        the current date and time if None. Note: this does not determine the OME-XML AcquisitionDate element value.
    :param channel_names: A list of channel names. If True, channel names are determined using the DataArray channel
        coordinate; if False, channel names are not set. If None, defaults to the behavior for True for DataArrays when
        writing multi-channel OME-TIFFs, and to the behavior for False otherwise. Only relevant when writing
        multi-channel OME-TIFF files, any value other than None or False will raise a warning for other TIFF profiles.
    :param description: TIFF description tag. Will default to the OME-XML header when writing OME-TIFF files. Any value
        other than None will raise a warning in this case.
    :param profile: TIFF specification of the written file.
        Supported TIFF profiles:
        - TIFF (no restrictions apply)
        - ImageJ (undocumented file format that is supported by the ImageJ software)
        - OME-TIFF (Open Microscopy Environment TIFF standard-compliant file format with minimal OME-XML header)
    :param big_endian: If true, stores data in big endian format, otherwise uses little endian byte order. If None, the
        byte order is set to True for the ImageJ TIFF profile and defaults to the system default otherwise.
    :param big_tiff: If True, enables support for writing files larger than 4GB. Not supported for TiffProfile.IMAGEJ.
    :param big_tiff_threshold: Threshold for enabling BigTIFF support when big_tiff is set to None, in bytes. Defaults
        to 4GB, minus 32MB for metadata.
    :param interleaved: If True, OME-TIFF images are saved as interleaved (this only affects OME-XML metadata). Always
        True for RGB(A) images (i.e., S=3 or 4) - a warning will be raised if explicitly set to False for RGB(A) images.
    :param compression_type: Compression algorithm, see tifffile.TIFF.COMPRESSION() for available values. Compression is
        not supported for TiffProfile.IMAGEJ. Note: Compression prevents from memory-mapping images and should therefore
        be avoided when images are compressed externally, e.g. when they are stored in compressed archives.
    :param compression_level: Compression level, between 0 and 9. Compression is not supported for TiffProfile.IMAGEJ.
        Note: Compression prevents from memory-mapping images and should therefore be avoided when images are compressed
        externally, e.g. when they are stored in compressed archives.
    :param pixel_size: Planar (x/y) size of one pixel, in micrometer.
    :param pixel_depth: Depth (z size) of one pixel, in micrometer. Only relevant when writing OME-TIFF files, any value
        other than None will raise a warning for other TIFF profiles.
    :param software: Name of the software used to create the file. Must be 7-bit ASCII. Saved with the first page only.
    :param ome_xml_fun: Function that will be used for generating the OME-XML header. See the default implementation for
        reference of the required signature. Only relevant when writing OME-TIFF files, ignored otherwise.
    :param ome_xml_kwargs: Optional arguments that are passed to the ome_xml_fun function. Only relevant when writing
        OME-TIFF files, will raise a warning if provided for other TIFF profiles.
    """
    # file
    if isinstance(file, str):
        file = Path(file)
    if isinstance(file, Path):
        if not file.suffix.lower() == '.tiff':
            warnings.warn('The specified TIFF file name does not end with .tiff: {}'.format(file))
        if profile == TiffProfile.OME_TIFF:
            if not file.name.lower().endswith('.ome.tiff'):
                warnings.warn('The specified OME-TIFF file name does not end with .ome.tiff: {}'.format(file))
        else:
            if file.name.lower().endswith('.ome.tiff'):
                warnings.warn('The specified non-OME-TIFF file name ends with .ome.tiff: {}'.format(file))

    # image name
    data_array_has_image_name = (_is_data_array(img) and img.name)
    if image_name is None and (data_array_has_image_name or isinstance(file, Path)) and profile == TiffProfile.OME_TIFF:
        image_name = True
    if isinstance(image_name, bool):
        if image_name:
            if data_array_has_image_name:
                image_name = img.name
            elif isinstance(file, Path):
                image_name = file.name
            else:
                raise ValueError('Cannot determine image name from non-DataArray images written to unknown file names')
        else:
            image_name = None
    if isinstance(image_name, str) and len(image_name) == 0:
        raise ValueError('Image name is empty')
    if image_name is not None and profile != TiffProfile.OME_TIFF:
        warnings.warn('The provided TIFF profile does not support image names, ignoring image name')
        image_name = None
    assert image_name is None or len(image_name) > 0

    # image date
    if image_date is None:
        image_date = datetime.now()

    # byte order
    if big_endian is None:
        big_endian = (profile == TiffProfile.IMAGEJ) or sys.byteorder == 'big'
    elif profile == TiffProfile.IMAGEJ and not big_endian:
        warnings.warn('The ImageJ TIFF profile does not support the specified byte order, continuing with big endian')
        big_endian = True
    assert big_endian is not None

    # compression
    if compression_type is not None and compression_type not in tifffile.TIFF.COMPRESSION():
        raise ValueError('The specified compression type is not supported: {}'.format(compression_type))
    if not 0 <= compression_level <= 9:
        raise ValueError('The specified compression level is not between 0 and 9: {:d}'.format(compression_level))
    compression = compression_level
    if compression_type is not None:
        compression = (compression_type, compression_level)
    if profile == TiffProfile.IMAGEJ and compression != 0:
        warnings.warn('The ImageJ TIFF profile does not support compression, ignoring compression')
        compression = 0
    assert isinstance(compression, int) or isinstance(compression, tuple) and len(compression) == 2

    # resolution
    resolution = None
    if pixel_size is not None:
        if pixel_size <= 0.:
            raise ValueError('The specified pixel size is not larger than zero: {:f}'.format(pixel_size))
        pixels_per_centimeter = 10 ** 4 / pixel_size
        resolution = (pixels_per_centimeter, pixels_per_centimeter, 'CENTIMETER')
    if pixel_depth is not None and profile != TiffProfile.OME_TIFF:
        warnings.warn('Pixel depth information is supported for OME-TIFF only, ignoring pixel depth')
        pixel_depth = None
    if pixel_depth is not None and pixel_depth <= 0:
        raise ValueError('The specified pixel depth is not larger than zero: {:f}'.format(pixel_size))

    # convert image to numpy array or xarray DataArray
    if not isinstance(img, np.ndarray) and not _is_data_array(img):
        img = np.asarray(img)
    if profile == TiffProfile.IMAGEJ and img.dtype not in (np.uint8, np.uint16, np.float32):
        fmt = 'The ImageJ TIFF profile does not support the specified data type: {} (supported: uint8, uint16, float32)'
        raise ValueError(fmt.format(str(img.dtype)))
    assert isinstance(img, np.ndarray) or _is_data_array(img)

    # determine image shape
    channel_axis = None
    img_shape = img.shape
    if img.ndim == 2:  # YX
        img_shape = (1, 1, 1, img.shape[0], img.shape[1], 1)
    elif img.ndim == 3:  # CYX
        channel_axis = 0
        img_shape = (1, 1, img.shape[0], img.shape[1], img.shape[2], 1)
    elif img.ndim == 4:  # ZCYX
        channel_axis = 1
        img_shape = (1, img.shape[0], img.shape[1], img.shape[2], img.shape[3], 1)
    elif img.ndim == 5:  # TZCYX
        channel_axis = 2
        img_shape = (img.shape[0], img.shape[1], img.shape[2], img.shape[3], img.shape[4], 1)
    elif img.ndim == 6:  # TZCYXS
        channel_axis = 2
        if img.shape[-1] > 1 and not interleaved:
            interleaved = True
            if profile == TiffProfile.OME_TIFF:
                warnings.warn('RGB(A) OME-TIFF images must be saved as interleaved, ignoring interleaved parameter')
    else:
        raise ValueError('Unsupported number of dimensions: {:d} (supported: 2, 3, 4, 5, 6)'.format(img.ndim))
    size_t, size_z, size_c, size_y, size_x, size_s = img_shape
    if profile == TiffProfile.IMAGEJ and size_s in (3, 4) and img.dtype != np.uint8:
        warnings.warn('The ImageJ TIFF profile for RGB does not support the specified data type, casting to uint8')
        img = img.astype(np.uint8)
    assert len(img_shape) == 6

    # determine channel names
    if channel_names is None and _is_data_array(img) and channel_axis is not None and profile == TiffProfile.OME_TIFF:
        channel_names = True
    if isinstance(channel_names, bool):
        if channel_names:
            if not _is_data_array(img):
                raise ValueError('Cannot determine channel names from non-DataArray image')
            if channel_axis is None:
                raise ValueError('Cannot determine channel names from DataArrays without a channel dimension')
            img: Any  # to "help" PyCharm dealing with DataArrays
            channel_names = img.coords[img.dims[channel_axis]].values
        else:
            channel_names = None
    if channel_names is not None and len(channel_names) != size_c:
        raise ValueError('Invalid number of channel names: {:d} (expected: {:d})'.format(len(channel_names), size_c))
    if channel_names is not None and profile != TiffProfile.OME_TIFF:
        warnings.warn('Channel names are supported for OME-TIFF only, ignoring channel names')
        channel_names = None
    assert channel_names is None or len(channel_names) == size_c

    # convert image to TZCYXS numpy array
    if _is_data_array(img):
        img = img.values
    img = img.reshape(img_shape)
    assert isinstance(img, np.ndarray) and len(img.shape) == 6

    # determine BigTIFF status
    if big_tiff_threshold < 0:
        raise ValueError('The BigTIFF size threshold is negative: {:d}'.format(big_tiff_threshold))
    if big_tiff is None:
        big_tiff = (img.size * img.itemsize > big_tiff_threshold)
    if big_tiff and profile == TiffProfile.IMAGEJ:
        warnings.warn('BigTIFF is not supported for ImageJ format, disabling BigTIFF')
        big_tiff = False
    assert big_tiff is not None

    # get description tag
    if description is not None and profile == TiffProfile.OME_TIFF:
        warnings.warn('Custom TIFF description tags are not supported for OME-TIFF, ignoring description')
        description = None
    if ome_xml_kwargs and profile != TiffProfile.OME_TIFF:
        warnings.warn('Additional arguments are supported for OME-TIFF only, ignoring additional keyword arguments')
        ome_xml_kwargs = {}
    if profile == TiffProfile.OME_TIFF:
        if ome_xml_fun is None:
            raise ValueError('No function provided for generating the OME-XML')
        ome_xml = ome_xml_fun(img, image_name, channel_names, big_endian, pixel_size, pixel_depth,
                              interleaved=interleaved, **ome_xml_kwargs)
        # While TIFF technically only supports ASCII, OME-XML requires UTF-8 encoding. In particular, the ASCII standard
        # does not support the micron (μ) character, which is used in PhysicalSizeX/Y/Z attributes. Therefore, the
        # OME-XML Description Tag is always encoded as UTF-8.
        with BytesIO() as description_buffer:
            ome_xml.write(description_buffer, encoding='utf-8', xml_declaration=True)
            description = description_buffer.getvalue()  # do not decode byte string to skip tifffile's ASCII check

    # write image
    byte_order = '>' if big_endian else '<'
    imagej = (profile == TiffProfile.IMAGEJ)
    metadata = None if profile == TiffProfile.OME_TIFF else {}
    with TiffWriter(file, bigtiff=big_tiff, byteorder=byte_order, imagej=imagej) as writer:
        # set photometric to 'MINISBLACK' to not treat three-channel images as RGB
        writer.save(data=img, photometric='MINISBLACK', compress=compression, description=description,
                    datetime=image_date, resolution=resolution, software=software, metadata=metadata)


def _is_data_array(img) -> bool:
    if xr is not None:
        return isinstance(img, xr.DataArray)
    return False
