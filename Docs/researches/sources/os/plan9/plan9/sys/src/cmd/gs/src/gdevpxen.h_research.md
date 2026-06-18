# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpxen.h

This header defines PCL XL enumerated attribute values. The values are written directly into the PCL XL stream, so enum numeric layout is part of the protocol contract.

Major enum groups:
- Geometry and drawing: arc direction, clip/fill mode, clip region, line cap, line join, pattern persistence, source transparency, and paint transparency.
- Color/image: color depth, color mapping, color space, compression mode, color treatment, halftone, trapping, and neutral-axis values.
- Data encoding: byte order/data organization, data source, and numeric data type.
- Page/media: measure units, media destination, media size, media source, media type, orientation, simplex/duplex modes, and duplex side.
- Text/font: character substitution and writing mode.
- Error reporting and device behavior.

Important macros:
- `pxeLineCap_to_library` maps PCL XL cap styles to Ghostscript line-cap values.
- `pxeLineJoin_to_library` maps PCL XL join styles to Ghostscript line-join values.
- `pxeMeasure_to_points` maps measure units to point conversion factors.
- `px_enumerate_media(m)` enumerates known paper sizes with size codes and width/height dimensions; `gdevpxut.c` uses this to match device dimensions to media-size codes.

This is protocol vocabulary, not executable logic, but it directly controls emitted PCL XL values.
