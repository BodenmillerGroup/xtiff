import numpy as np
import pytest

from io import BytesIO
from xml.etree import ElementTree
from xtiff import get_ome_xml

ElementTree.register_namespace('', 'http://www.openmicroscopy.org/Schemas/OME/2016-06')


@pytest.fixture
def expected_ome_xml_str_py38():
    return """<?xml version='1.0' encoding='ascii'?>
<OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openmicroscopy.org/Schemas/OME/2016-06 http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd"><Image ID="Image:0" Name="image.tiff"><Pixels ID="Pixels:0" Type="double" SizeX="200" SizeY="200" SizeC="10" SizeZ="1" SizeT="1" DimensionOrder="XYCZT" Interleaved="true" BigEndian="false"><Channel ID="Channel:0:0" SamplesPerPixel="1" Name="Channel 1" /><Channel ID="Channel:0:1" SamplesPerPixel="1" Name="Channel 2" /><Channel ID="Channel:0:2" SamplesPerPixel="1" Name="Channel 3" /><Channel ID="Channel:0:3" SamplesPerPixel="1" Name="Channel 4" /><Channel ID="Channel:0:4" SamplesPerPixel="1" Name="Channel 5" /><Channel ID="Channel:0:5" SamplesPerPixel="1" Name="Channel 6" /><Channel ID="Channel:0:6" SamplesPerPixel="1" Name="Channel 7" /><Channel ID="Channel:0:7" SamplesPerPixel="1" Name="Channel 8" /><Channel ID="Channel:0:8" SamplesPerPixel="1" Name="Channel 9" /><Channel ID="Channel:0:9" SamplesPerPixel="1" Name="Channel 10" /><TiffData /></Pixels></Image></OME>"""


def test_get_ome_xml(expected_ome_xml_str_py38):
    num_channels = 10
    img = np.zeros((1, 1, num_channels, 200, 200, 1))
    channel_names = [f'Channel {i + 1}' for i in range(num_channels)]
    ome_xml = get_ome_xml(img, 'image.tiff', channel_names, False, None, None)
    with BytesIO() as description_buffer:
        ome_xml.write(description_buffer, encoding='ascii', xml_declaration=True)
        description = description_buffer.getvalue().decode('ascii')
    expected_ome_xml = ElementTree.ElementTree(element=ElementTree.fromstring(expected_ome_xml_str_py38))
    with BytesIO() as expected_description_buffer:
        expected_ome_xml.write(expected_description_buffer, encoding='ascii', xml_declaration=True)
        expected_description = expected_description_buffer.getvalue().decode('ascii')
    assert description == expected_description
