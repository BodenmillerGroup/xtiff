from io import BytesIO
from typing import Optional, Sequence, Union

import numpy as np
import os
import re
import string
import sys
import tifffile
import warnings
import xml.etree.ElementTree as ET

from datetime import datetime
from enum import Enum
from tifffile import TiffWriter

try:
    import xarray as xr
except ImportError:
    xr = None


class WriteMode(Enum):
    TIFF = 1
    IMAGEJ = 2
    OME_TIFF = 3


class ByteOrder(Enum):
    LITTLE_ENDIAN = '<'
    BIG_ENDIAN = '>'


OME_XML_TEMPLATE_201606V2 = os.path.join(os.path.dirname(__file__), 'ome201606v2.xml')
OME_TYPES = {
    np.bool: 'bool',
    np.int8().dtype: 'int8',
    np.int16().dtype: 'int16',
    np.int32().dtype: 'int32',
    np.uint8().dtype: 'uint8',
    np.uint16().dtype: 'uint16',
    np.uint32().dtype: 'uint32',
    np.float32().dtype: 'float',
    np.float64().dtype: 'double',
}


class PartialFormatter(string.Formatter):
    def __init__(self, default='{{{0}}}'):
        self.default = default

    def get_value(self, key, args, kwargs):
        if isinstance(key, str):
            return kwargs.get(key, self.default.format(key))
        else:
            return super(PartialFormatter, self).get_value(key, args, kwargs)


def _is_data_array(img) -> bool:
    if xr is not None:
        return isinstance(img, xr.DataArray)
    return False


_OME_CHANNEL_XML_FMT = '<Channel ID="Channel:0:{id:d}" SamplesPerPixel="{samples_per_pixel:d}"{channel_extra} />'
_OME_IMAGE_NAME_EXTRA_FMT = ' Name="{name}"'
_OME_PIXELS_PHYSICAL_SIZE_XY_EXTRA_FMT = ' PhysicalSizeX="{x:f}" PhysicalSizeY="{y:f}"'
_OME_PIXELS_PHYSICAL_SIZE_Z_EXTRA_FMT = ' PhysicalSizeZ="{z:f}"'
_OME_CHANNEL_NAME_EXTRA_FMT = ' Name="{name}"'


def get_ome_xml(img: np.ndarray, image_name: Optional[str], channel_names: Optional[Sequence[str]],
                byte_order: ByteOrder, pixel_size: Optional[float], pixel_depth: Optional[float],
                ome_xml_template_file_path: str, **kwargs) -> ET.Element:
    with open(ome_xml_template_file_path, 'r') as ome_xml_template_file:
        ome_xml_template = ome_xml_template_file.read()
    size_t, size_z, size_c, size_y, size_x, size_s = img.shape
    image_extra = ''
    if image_name:
        image_extra += _OME_IMAGE_NAME_EXTRA_FMT.format(name=image_name)
    pixels_extra = ''
    if pixel_size is not None:
        pixels_extra += _OME_PIXELS_PHYSICAL_SIZE_XY_EXTRA_FMT.format(x=pixel_size, y=pixel_size)
    if pixel_depth is not None:
        pixels_extra += _OME_PIXELS_PHYSICAL_SIZE_Z_EXTRA_FMT.format(z=pixel_depth)
    ome_channel_xml = ''
    for channel_id in range(size_c):
        channel_extra = ''
        if channel_names is not None and channel_names[channel_id]:
            channel_extra += _OME_CHANNEL_NAME_EXTRA_FMT.format(name=channel_names[channel_id])
        ome_channel_xml += _OME_CHANNEL_XML_FMT.format(id=channel_id, samples_per_pixel=size_s,
                                                       channel_extra=channel_extra)
    ome_xml = PartialFormatter().format(
        ome_xml_template,
        type=OME_TYPES[img.dtype], big_endian=(byte_order == ByteOrder.BIG_ENDIAN),
        size_x=size_x, size_y=size_y, size_c=size_c, size_z=size_z, size_t=size_t,
        image_extra=image_extra, pixels_extra=pixels_extra, channel_xml=ome_channel_xml
    )
    return ET.fromstring(ome_xml)


def to_tiff(img, file, image_name: Optional[str] = None, channel_names: Optional[Union[Sequence[str], str]] = None,
            image_date: Optional[Union[str, datetime]] = None, write_mode: WriteMode = WriteMode.OME_TIFF,
            big_tiff: Optional[bool] = None, big_tiff_size_threshold: int = 2 ** 32 - 2 ** 25,
            byte_order: Optional[ByteOrder] = None, compression_type: Optional[str] = None, compression_level: int = 0,
            pixel_size: Optional[float] = None, pixel_depth: Optional[float] = None,
            ome_xml=get_ome_xml, ome_xml_template: str = OME_XML_TEMPLATE_201606V2, **ome_xml_kwargs) -> None:
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
        - any numpy data type in TIFF write mode
        - uint8, uint16, float32 in ImageJ write mode (uint8 for RGB images)
        - bool, int8, int16, int32, uint8, uint16, uint32, float32, float64 in OME-TIFF write mode
    :param file: File target supported by tifffile TiffWriter, e.g. path to file (str) or binary stream.
    :param image_name: Image name for OME-TIFF images. Defaults to the DataArray name (if img is a DataArray) or to the
        file name (if file is a str) if None, or is ignored if no default value is available. Only relevant when writing
        OME-TIFF files, any value other than None will raise a warning for other write modes.
    :param channel_names: A list of channel names or the name of the DataArray coordinate containing the channel names.
        Only relevant when writing OME-TIFF files, any value other than None will raise a warning for other write modes.
    :param image_date: Date and time of image creation in '%Y:%m:%d %H:%M:%S' format or as datetime object. Defaults to
        the current date and time if None. Note: this does not correspond to the OME-TIFF acquisition date.
    :param write_mode: TIFF format/standard of the written file.
        Supported write modes:
        - TIFF (no restrictions apply)
        - ImageJ (undocumented file format that is supported by the ImageJ software)
        - OME-TIFF (Open Microscopy Environment TIFF standard-compliant file format with minimal OME-XML header)
    :param big_tiff: If True, enables support for writing files larger than 4GB. Not supported in ImageJ write mode.
    :param big_tiff_size_threshold: Threshold for enabling BigTIFF support when big_tiff is set to None, in bytes.
        Defaults to 4GB - 32MB for metadata.
    :param byte_order: Byte order of the written file.
    :param compression_type: Compression algorithm, see tifffile.TIFF.COMPRESSION() for available values. Compression
        is not supported in ImageJ write mode. Note: Compression prevents from memory-mapping images and should
        therefore be avoided when images are compressed externally, e.g. when they are stored in compressed archives.
    :param compression_level: Compression level, between 0 and 9. Compression is not supported in ImageJ write mode.
        Note: Compression prevents from memory-mapping images and should therefore be avoided when images are compressed
        externally, e.g. when they are stored in compressed archives.
    :param pixel_size: Planar (x/y) size of one pixel, in micrometer.
    :param pixel_depth: Depth (z size) of one pixel, in micrometer. Only relevant when writing OME-TIFF files, any value
        other than None will raise a warning for other write modes.
    :param ome_xml: Function that will be used for generating the OME-XML header. See the default implementation for
        reference of the required signature. Only relevant when writing OME-TIFF files, ignored otherwise.
    :param ome_xml_template: Path to the OME-XML template file containing the Python format string that will be passed
        to ome_xml_fun. See the default value for reference of the available placeholders. Only relevant when writing
        OME-TIFF files, ignored otherwise.
    :param ome_xml_kwargs: Optional arguments that are passed to ome_xml. Only relevant when writing OME-TIFF files,
        will raise a warning if provided for other write modes.
    """
    # check file name
    if isinstance(file, str):
        if not file.endswith('.tiff'):
            warnings.warn('The provided TIFF file name does not end with .tiff: {}'.format(file))
        if write_mode == WriteMode.OME_TIFF:
            if not file.endswith('.ome.tiff'):
                warnings.warn('The provided OME-TIFF file name does not end with .ome.tiff: {}'.format(file))
        else:
            if file.endswith('.ome.tiff'):
                warnings.warn('The provided non-OME-TIFF file name ends with .ome.tiff: {}'.format(file))

    # prepare image name
    if image_name is None:
        if _is_data_array(img) and img.name:
            image_name = img.name
        elif isinstance(file, str):
            image_name = os.path.basename(file)
    elif write_mode != WriteMode.OME_TIFF:
        warnings.warn('The provided write mode does not consider image names, ignoring image name')
        image_name = None
    assert image_name is None or len(image_name) > 0

    # prepare image date
    if image_date is None:
        image_date = datetime.now()

    # prepare byte order
    if byte_order is None:
        if write_mode == WriteMode.IMAGEJ:
            byte_order = ByteOrder.BIG_ENDIAN
        else:
            byte_order = ByteOrder.LITTLE_ENDIAN if sys.byteorder == 'little' else ByteOrder.BIG_ENDIAN
    elif write_mode == WriteMode.IMAGEJ and byte_order != ByteOrder.BIG_ENDIAN:
        warnings.warn('The ImageJ format does not support the provided byte order, continuing with big endian')
        byte_order = ByteOrder.BIG_ENDIAN
    assert byte_order is not None

    # prepare compression
    if compression_type is not None and compression_type not in tifffile.TIFF.COMPRESSION():
        raise ValueError('The provided compression type is not supported: {}'.format(compression_type))
    if not 0 <= compression_level <= 9:
        raise ValueError('The provided compression level is not between 0 and 9: {:d}'.format(compression_level))
    compression = compression_level
    if compression_type is not None:
        compression = (compression_type, compression_level)
    if write_mode == WriteMode.IMAGEJ and compression != 0:
        warnings.warn('The ImageJ format does not support compression, writing uncompressed')
        compression = 0
    assert isinstance(compression, int) or isinstance(compression, tuple) and len(compression) == 2

    # prepare resolution
    resolution = None
    if pixel_size is not None:
        if pixel_size <= 0.:
            raise ValueError('The provided pixel size is not larger than zero: {:f}'.format(pixel_size))
        pixels_per_centimeter = 10 ** 4 / pixel_size
        resolution = (pixels_per_centimeter, pixels_per_centimeter, 'CENTIMETER')
    if pixel_depth is not None and write_mode != WriteMode.OME_TIFF:
        warnings.warn('Pixel depth information is supported for OME-TIFF only, ignoring pixel depth information')
        pixel_depth = None
    if pixel_depth is not None and pixel_depth <= 0:
        raise ValueError('The provided pixel depth is not larger than zero: {:f}'.format(pixel_size))

    # prepare image (afterwards, img will be a numpy array or an xarray DataArray)
    if not isinstance(img, np.ndarray) and not _is_data_array(img):
        img = np.asarray(img)
    if write_mode == WriteMode.IMAGEJ and img.dtype not in (np.uint8, np.uint16, np.float32):
        fmt = 'The ImageJ format does not support the provided data type: {} (supported: uint8, uint16, float32)'
        raise ValueError(fmt.format(str(img.dtype)))
    assert isinstance(img, np.ndarray) or _is_data_array(img)

    # determine image shape
    img_shape = img.shape
    if img.ndim == 2:  # YX
        img_shape = (1, 1, 1, img.shape[0], img.shape[1], 1)
    elif img.ndim == 3:  # CYX
        img_shape = (1, 1, img.shape[0], img.shape[1], img.shape[2], 1)
    elif img.ndim == 4:  # ZCYX
        img_shape = (1, img.shape[0], img.shape[1], img.shape[2], img.shape[3], 1)
    elif img.ndim == 5:  # TZCYZ
        img_shape = (img.shape[0], img.shape[1], img.shape[2], img.shape[3], img.shape[4], 1)
    elif img.ndim > 6:
        raise ValueError('Invalid number of dimensions: {:d} (supported: 2, 3, 4, 5, 6)'.format(img.ndim))
    size_t, size_z, size_c, size_y, size_x, size_s = img_shape
    if write_mode == WriteMode.IMAGEJ and size_s in (3, 4) and img.dtype != np.uint8:
        warnings.warn('The ImageJ format for RGB images does not support the provided data type, casting to uint8')
        img = img.astype(np.uint8)
    assert len(img_shape) == 6

    # prepare channel names
    if channel_names is not None and write_mode != WriteMode.OME_TIFF:
        warnings.warn('Channel names are supported for OME-TIFF only, ignoring channel names')
        channel_names = None
    if channel_names is not None:
        if isinstance(channel_names, str):
            if not _is_data_array(img):
                raise ValueError('Channel name coordinates are supported for DataArrays only')
            if channel_names not in img.coords:
                raise ValueError('Channel name coordinate not found in DataArray: {}'.format(channel_names))
            channel_names = img.coords[channel_names].values
        if len(channel_names) != size_c:
            fmt = 'Invalid number of channel names: {:d} (expected: {:d})'
            raise ValueError(fmt.format(len(channel_names), size_c))
    assert channel_names is None or len(channel_names) == size_c

    # reshape to TZCYXS (afterwards, img will be a numpy array)
    if _is_data_array(img):
        img = img.values
    img = img.reshape(img_shape)
    assert isinstance(img, np.ndarray) and len(img.shape) == 6

    # prepare BigTIFF support
    if big_tiff_size_threshold < 0:
        raise ValueError('The BigTIFF size threshold is negative: {:d}'.format(big_tiff_size_threshold))
    if big_tiff is None:
        big_tiff = (img.size * img.itemsize > big_tiff_size_threshold)
    if big_tiff and write_mode == WriteMode.IMAGEJ:
        warnings.warn('BigTIFF is not supported for ImageJ format, disabling BigTIFF')
        big_tiff = False
    assert big_tiff is not None

    # prepare description
    description = None
    if ome_xml_kwargs and write_mode != WriteMode.OME_TIFF:
        warnings.warn('Additional arguments are supported for OME-TIFF only, ignoring additional arguments')
        ome_xml_kwargs = {}
    if write_mode == WriteMode.OME_TIFF:
        ome_xml_element = ome_xml(img, image_name, channel_names, byte_order, pixel_size, pixel_depth, ome_xml_template,
                                  **ome_xml_kwargs)
        ome_xml_ns_match = re.search('{.*}', ome_xml_element.tag)
        if ome_xml_ns_match:
            ome_xml_ns = ome_xml_ns_match.group(0)[1:-1]
            ET.register_namespace('', ome_xml_ns)
        ome_xml_tree = ET.ElementTree(element=ome_xml_element)
        with BytesIO() as ome_xml_buffer:
            ome_xml_tree.write(ome_xml_buffer, encoding='utf8', xml_declaration=True)
            description = ome_xml_buffer.getvalue().decode('utf8')

    # write image
    with TiffWriter(file, imagej=(write_mode == WriteMode.IMAGEJ), bigtiff=big_tiff, byteorder=byte_order.value) as tw:
        tw.save(img, compress=compression, description=description, datetime=image_date, resolution=resolution)
