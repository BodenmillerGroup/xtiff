# xtiff

![PyPI](https://img.shields.io/pypi/v/xtiff)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/xtiff)
![PyPI - License](https://img.shields.io/pypi/l/xtiff)
![Codecov](https://img.shields.io/codecov/c/github/BodenmillerGroup/xtiff)
![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/BodenmillerGroup/xtiff/test-and-deploy/master)
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

This package requires Python 3.7 or later.

Python package dependencies are listed in [requirements.txt](https://github.com/BodenmillerGroup/xtiff/blob/master/requirements.txt).

Using virtual environments is strongly recommended.

## Installation

Install xtiff and its dependencies with:

    pip install xtiff


## Usage

The package provides the following main function for writing TIFF files:

    to_tiff(img, file, image_name=None, image_date=None, channel_names=None, description=None,
            profile=TiffProfile.OME_TIFF, big_endian=None, big_tiff=None, big_tiff_threshold=4261412864,
            compression_type=None, compression_level=0, pixel_size=None, pixel_depth=None,
            software='xtiff', ome_xml_fun=get_ome_xml, **ome_xml_kwargs):

In addition, `get_ome_xml()` is provided as the default OME-XML-generating function.

Documentation of the function parameters is available via Python's internal help system: `help(xtiff.to_tiff)`

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
