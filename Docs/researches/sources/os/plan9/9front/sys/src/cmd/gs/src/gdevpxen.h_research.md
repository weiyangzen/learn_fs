# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpxen.h

This header defines PCL XL enumerated attribute values.

Major enum groups:
- Geometry and drawing: arc direction, clip/fill mode, clip region, line cap, line join, pattern persistence, source/paint transparency.
- Color/image: color depth, color mapping, color space, compression mode, color treatment, halftone/trapping values.
- Data encoding: byte order/data organization, data source, numeric data type.
- Page/media: measure units, media destination, media size, media source, media type, orientation, simplex/duplex modes, duplex side.
- Text/font: character substitution and writing mode.
- Error reporting and device behavior.

Important macros:
- `pxeLineCap_to_library`, `pxeLineJoin_to_library`, and `pxeMeasure_to_points` map protocol values to Ghostscript/library values.
- `px_enumerate_media(m)` enumerates known paper sizes with dimensions and resolution basis. `gdevpxut.c` uses this macro to match device dimensions to PCL XL media size codes.

This is a protocol vocabulary header for `gdevpx.c` and `gdevpxut.c`.
