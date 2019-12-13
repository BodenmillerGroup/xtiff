# xtiff

A tiny Python 3 library for writing multi-channel TIFF stacks.

The aim of this library is to provide an easy way to write multi-channel image stacks for external visualization and
analysis. It acts as an interface to the popular [tifffile](https://www.lfd.uci.edu/~gohlke/) package and supports
[xarray](http://xarray.pydata.org) DataArrays as well as [numpy](https://www.numpy.org)-compatible data structures.

To maximize compatibility with third-party software, the images are written in standard-compliant fashion, with minimal
metadata and in TZCYX channel order. In particular, a minimal (but extensible) subset of the OME-TIFF standard is
supported, enabling the naming of channels.

## Installation

Install from pypi:

`pip install xtiff`


## Usage

The package provides the following main function for writing TIFF files:

```python3
to_tiff(img, file, image_name=None, channel_names=None, image_date=None,
        write_mode=WriteMode.OME_TIFF, big_tiff=None, big_tiff_size_threshold=4294967246, 
        byte_order=None, compression_type=None, compression_level=0, pixel_size=None,
        pixel_depth=None, ome_xml=get_ome_xml, ome_xml_template=OME_XML_TEMPLATE_201606V2
        **ome_xml_kwargs)
```

Documentation of the function parameters is available via Python's internal help system: `help(xtiff.to_tiff)`

In addition, the function `get_ome_xml()` is provided as the default OME-XML-generating function.

## FAQ

_Why should I care about TIFF? I use Zarr/NetCDF/whatever._

That's good! TIFF is an old and complex file format, has many disadvantages and is impractical for storing large images.
However, it also remains one of the most widely used scientific image formats and is (at least partially) supported by
many popular tools, such as ImageJ. With xtiff, you can continue to store your images in your favorite file format,
while having the opportunity to easily convert them to a format that can be read by (almost) any tool.

_Why can't I use the tifffile package directly?_

Of course you can! Christoph Gohlke's [tifffile](https://www.lfd.uci.edu/~gohlke/) package provides a very powerful and
feature-complete interface for writing TIFF files and is the backend for xtiff. Essentially, the xtiff package is just a
wrapper for tifffile. While you can in principle write any image directly with tifffile, in many cases, the flexibility
of the TIFF format can be daunting. The xtiff package reduces the configuration burden and metadata to an essential
minimum.

## Change log

2019-12-12 v0.1.2 - Initial release  
2019-12-12 v0.2.1 - Expose OME-XML to user  
2019-12-12 v0.2.2 - Support for ome_xml_kwargs  
2019-12-13 v0.3.0 - Simplified to_tiff interface  

## License

This project is licensed under the [MIT license](https://github.com/BodenmillerGroup/xtiff/blob/master/LICENSE.txt).