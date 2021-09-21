# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.7.7] - 2021-09-21

Expose xtiff.TiffProfile ([#9](https://github.com/BodenmillerGroup/xtiff/issues/9))

## [v0.7.6] - 2021-06-06

Encode OME-XML as UTF-8

## [v0.7.5] - 2021-05-27

Make OME-XML PixelSizeXUnit, PixelSizeYUnit, PixelSizeZUnit attribute values explicit (set to µm)

## [v0.7.4] - 2021-05-20

Fix interleaving parameter & warnings

## [v0.7.3] - 2021-05-20

Added interleaved parameter to to_tiff function (for better backwards compatibility)

## [v0.7.2] - 2021-05-20

Save grayscale OME-TIFF images as non-interleaved (closes [#7](https://github.com/BodenmillerGroup/xtiff/issues/7))

## [v0.7.1] - 2021-03-16

Added support for Python 3.7

## [v0.7.0] - 2021-03-15

Restructured package, added tests, require Python 3.8+, fix issue [#5](https://github.com/BodenmillerGroup/xtiff/issues/5)

## [v0.6.4] - 2021-01-20

Fixed bug related to issue [#4](https://github.com/BodenmillerGroup/xtiff/issues/4)

## [v0.6.3] - 2021-01-20

Fixed OME-XML encoding issue [#4](https://github.com/BodenmillerGroup/xtiff/issues/4)

## [v0.6.2] - 2020-08-14

Fixed tifffile compatibility, added software parameter

## [v0.6.1] - 2020-01-23

Small bug fix in dimension checking

## [v0.6.0] - 2020-01-23 

Switched to full XML tree for OME-XML generation

## [v0.5.0] - 2020-01-15

Simplified interface for OME-XML generation

## [v0.4.2] - 2020-01-13

Fixed package installation problems

## [v0.4.1] - 2020-01-13

Fixed XML encoding and XSD compliance

## [v0.4.0] - 2019-12-15

Added description parameter

## [v0.3.0] - 2019-12-13

Simplified to_tiff interface

## [v0.2.2] - 2019-12-12

Support for ome_xml_kwargs

## [v0.2.1] - 2019-12-12

Expose OME-XML to user

## [v0.1.2] - 2019-12-12

Initial release


[v0.7.7]: https://github.com/BodenmillerGroup/xtiff/compare/v0.7.6...v0.7.7
[v0.7.6]: https://github.com/BodenmillerGroup/xtiff/compare/v0.7.5...v0.7.6
[v0.7.5]: https://github.com/BodenmillerGroup/xtiff/compare/v0.7.4...v0.7.5
[v0.7.4]: https://github.com/BodenmillerGroup/xtiff/compare/v0.7.3...v0.7.4
[v0.7.3]: https://github.com/BodenmillerGroup/xtiff/compare/v0.7.2...v0.7.3
[v0.7.2]: https://github.com/BodenmillerGroup/xtiff/compare/v0.7.1...v0.7.2
[v0.7.1]: https://github.com/BodenmillerGroup/xtiff/compare/v0.7.0...v0.7.1
[v0.7.0]: https://github.com/BodenmillerGroup/xtiff/compare/v0.6.4...v0.7.0
[v0.6.4]: https://github.com/BodenmillerGroup/xtiff/compare/v0.6.3...v0.6.4
[v0.6.3]: https://github.com/BodenmillerGroup/xtiff/compare/v0.6.2...v0.6.3
[v0.6.2]: https://github.com/BodenmillerGroup/xtiff/compare/v0.6.1...v0.6.2
[v0.6.1]: https://github.com/BodenmillerGroup/xtiff/compare/v0.6.0...v0.6.1
[v0.6.0]: https://github.com/BodenmillerGroup/xtiff/compare/v0.5.0...v0.6.0
[v0.5.0]: https://github.com/BodenmillerGroup/xtiff/compare/v0.4.2...v0.5.0
[v0.4.2]: https://github.com/BodenmillerGroup/xtiff/compare/v0.4.1...v0.4.2
[v0.4.1]: https://github.com/BodenmillerGroup/xtiff/compare/v0.4.0...v0.4.1
[v0.4.0]: https://github.com/BodenmillerGroup/xtiff/compare/v0.3.0...v0.4.0
[v0.3.0]: https://github.com/BodenmillerGroup/xtiff/compare/v0.2.2...v0.3.0
[v0.2.2]: https://github.com/BodenmillerGroup/xtiff/compare/v0.2.1...v0.2.2
[v0.2.1]: https://github.com/BodenmillerGroup/xtiff/compare/v0.1.2...v0.2.1
[v0.1.2]: https://github.com/BodenmillerGroup/xtiff/releases/tag/v0.1.2
