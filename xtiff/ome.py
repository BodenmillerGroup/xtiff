import numpy as np

from typing import Optional, Sequence
from xml.etree import ElementTree

OME_TYPES = {
    np.bool_().dtype: 'bool',
    np.int8().dtype: 'int8',
    np.int16().dtype: 'int16',
    np.int32().dtype: 'int32',
    np.uint8().dtype: 'uint8',
    np.uint16().dtype: 'uint16',
    np.uint32().dtype: 'uint32',
    np.float32().dtype: 'float',
    np.float64().dtype: 'double',
}


def get_ome_xml(img: np.ndarray, image_name: Optional[str], channel_names: Optional[Sequence[str]], big_endian: bool,
                pixel_size: Optional[float], pixel_depth: Optional[float], **ome_xml_kwargs) -> ElementTree.ElementTree:
    size_t, size_z, size_c, size_y, size_x, size_s = img.shape
    if channel_names is not None:
        assert len(channel_names) == size_c
    if pixel_size is not None:
        assert pixel_size > 0.
    if pixel_depth is not None:
        assert pixel_depth > 0
    ome_namespace = 'http://www.openmicroscopy.org/Schemas/OME/2016-06'
    ome_schema_location = 'http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd'
    ome_element = ElementTree.Element('OME', attrib={
        'xmlns': ome_namespace,
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation': ' '.join((ome_namespace, ome_schema_location))
    })
    image_element = ElementTree.SubElement(ome_element, 'Image', attrib={
        'ID': 'Image:0',
    })
    if image_name is not None:
        image_element.set('Name', image_name)
    pixels_element = ElementTree.SubElement(image_element, 'Pixels', attrib={
        'ID': 'Pixels:0',
        'Type': OME_TYPES[img.dtype],
        'SizeX': str(size_x),
        'SizeY': str(size_y),
        'SizeC': str(size_c),
        'SizeZ': str(size_z),
        'SizeT': str(size_t),
        'DimensionOrder': 'XYCZT',
        'Interleaved': 'true',
        'BigEndian': 'true' if big_endian else 'false',
    })
    if pixel_size is not None:
        pixels_element.set('PhysicalSizeX', str(pixel_size))
        pixels_element.set('PhysicalSizeY', str(pixel_size))
    if pixel_depth is not None:
        pixels_element.set('PhysicalSizeZ', str(pixel_depth))
    for channel_id in range(size_c):
        channel_element = ElementTree.SubElement(pixels_element, 'Channel', attrib={
            'ID': 'Channel:0:{:d}'.format(channel_id),
            'SamplesPerPixel': str(size_s),
        })
        if channel_names is not None and channel_names[channel_id]:
            channel_element.set('Name', channel_names[channel_id])
    ElementTree.SubElement(pixels_element, 'TiffData')
    return ElementTree.ElementTree(element=ome_element)
