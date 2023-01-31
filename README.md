# xtiff

![PyPI](https://img.shields.io/pypi/v/xtiff)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/xtiff)
![PyPI - License](https://img.shields.io/pypi/l/xtiff)
![Codecov](https://img.shields.io/codecov/c/github/BodenmillerGroup/xtiff)
![GitHub Workflow Status (branch)](https://img.shields.io/github/actions/workflow/status/BodenmillerGroup/xtiff/build.yml)
![GitHub issues](https://img.shields.io/github/issues/BodenmillerGroup/xtiff)
![GitHub pull requests](https://img.shields.io/github/issues-pr/BodenmillerGroup/xtiff)

A tiny Python library for writing multi-channel TIFF stacks.

The aim of this library is to provide an easy way to write multi-channel image stacks for external visualization and
analysis. It acts as an interface to the popular [tifffile](https://www.lfd.uci.edu/~gohlke/) package and supports
[xarray](http://xarray.pydata.org) DataArrays as well as [numpy](https://www.numpy.org)-compatible data structures.

To maximize compatibility with third-party software, the images are written in standard-compliant fashion, with minimal
metadata and in TZCYX channel order. In particular, a minimal (but customizable) subset of the OME-TIFF standard is
supported, enabling the naming of channels.

## Requirements

This package requires Python 3.8 or newer.

Using virtual environments is strongly recommended.

## Installation

Install xtiff and its dependencies with:

    pip install xtiff


## Usage

The package provides the following main function for writing TIFF files:

    to_tiff(img, file, image_name=None, image_date=None, channel_names=None, description=None,
            profile=TiffProfile.OME_TIFF, big_endian=None, big_tiff=None, big_tiff_threshold=4261412864,
            compression_type=None, compression_level=0, pixel_size=None, pixel_depth=None,
            interleaved=True, software='xtiff', ome_xml_fun=get_ome_xml, **ome_xml_kwargs)


    img: The image to write, as xarray DataArray or numpy-compatible data structure.
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

    file: File target supported by tifffile TiffWriter, e.g. path to file (str, pathlib.Path) or binary stream.

    image_name: Image name for OME-TIFF images. If True, the image name is determined using the DataArray name or
        the file name (in that order); if False, the image name is not set. If None, defaults to the behavior for True
        for named DataArrays and when the file path is provided, and to the behavior of False otherwise. Only relevant
        when writing OME-TIFF files, any value other than None or False will raise a warning for other TIFF profiles.

    image_date: Date and time of image creation in '%Y:%m:%d %H:%M:%S' format or as datetime object. Defaults to
        the current date and time if None. Note: this does not determine the OME-XML AcquisitionDate element value.

    channel_names: A list of channel names. If True, channel names are determined using the DataArray channel
        coordinate; if False, channel names are not set. If None, defaults to the behavior for True for DataArrays when
        writing multi-channel OME-TIFFs, and to the behavior for False otherwise. Only relevant when writing
        multi-channel OME-TIFF files, any value other than None or False will raise a warning for other TIFF profiles.

    description: TIFF description tag. Will default to the OME-XML header when writing OME-TIFF files. Any value
        other than None will raise a warning in this case.

    profile: TIFF specification of the written file.
        Supported TIFF profiles:
        - TIFF (no restrictions apply)
        - ImageJ (undocumented file format that is supported by the ImageJ software)
        - OME-TIFF (Open Microscopy Environment TIFF standard-compliant file format with minimal OME-XML header)

    big_endian: If true, stores data in big endian format, otherwise uses little endian byte order. If None, the
        byte order is set to True for the ImageJ TIFF profile and defaults to the system default otherwise.

    big_tiff: If True, enables support for writing files larger than 4GB. Not supported for TiffProfile.IMAGEJ.

    big_tiff_threshold: Threshold for enabling BigTIFF support when big_tiff is set to None, in bytes. Defaults
        to 4GB, minus 32MB for metadata.

    compression_type: Compression algorithm, see tifffile.TIFF.COMPRESSION() for available values. Compression is
        not supported for TiffProfile.IMAGEJ. Note: Compression prevents from memory-mapping images and should therefore
        be avoided when images are compressed externally, e.g. when they are stored in compressed archives.

    compression_level: Compression level, between 0 and 9. Compression is not supported for TiffProfile.IMAGEJ.
        Note: Compression prevents from memory-mapping images and should therefore be avoided when images are compressed
        externally, e.g. when they are stored in compressed archives.

    pixel_size: Planar (x/y) size of one pixel, in micrometer.

    pixel_depth: Depth (z size) of one pixel, in micrometer. Only relevant when writing OME-TIFF files, any value
        other than None will raise a warning for other TIFF profiles.

    interleaved: If True, OME-TIFF images are saved as interleaved (this only affects OME-XML metadata). Always
        True for RGB(A) images (i.e., S=3 or 4) - a warning will be raised if explicitly set to False for RGB(A) images.

    software: Name of the software used to create the file. Must be 7-bit ASCII. Saved with the first page only.

    ome_xml_fun: Function that will be used for generating the OME-XML header. See the default implementation for
        reference of the required signature. Only relevant when writing OME-TIFF files, ignored otherwise.

    ome_xml_kwargs: Optional arguments that are passed to the ome_xml_fun function. Only relevant when writing
        OME-TIFF files, will raise a warning if provided for other TIFF profiles.

In addition, `get_ome_xml()` is provided as the default OME-XML-generating function.

## FAQ

**What metadata is included in the written images?**

In general, written metadata is kept at a minimum and only information that can be inferred from the raw image data is
included (image dimensions, data type, number of channels, channel names for xarrays). Additional metadata natively supported by the
tifffile package can be specified using function parameters. For OME-TIFF files, the OME-XML "Description" tag contents
can be further refined by specifying custom OME-XML-generating functions.

**Why should I care about TIFF? I use Zarr/NetCDF/whatever.**

That's good! TIFF is an old and complex file format, has many disadvantages and is impractical for storing large images.
However, it also remains one of the most widely used scientific image formats and is (at least partially) supported by
many popular tools, such as ImageJ. With xtiff, you can continue to store your images in your favorite file format,
while having the opportunity to easily convert them to a format that can be read by (almost) any tool.

**Why can't I use the tifffile package directly?**

Of course you can! Christoph Gohlke's [tifffile](https://www.lfd.uci.edu/~gohlke/) package provides a very powerful and
feature-complete interface for writing TIFF files and is the backend for xtiff. Essentially, the xtiff package is just a
wrapper for tifffile. While you can in principle write any image directly with tifffile, in many cases, the flexibility
of the TIFF format can be daunting. The xtiff package reduces the configuration burden and metadata to an essential
minimum.

## Authors

Created and maintained by Jonas Windhager [jonas.windhager@uzh.ch](mailto:jonas.windhager@uzh.ch)

## Contributing

[Contributing](https://github.com/BodenmillerGroup/xtiff/blob/master/CONTRIBUTING.md)

## Changelog

[Changelog](https://github.com/BodenmillerGroup/xtiff/blob/master/CHANGELOG.md)

## License

[MIT](https://github.com/BodenmillerGroup/xtiff/blob/master/LICENSE.md)
