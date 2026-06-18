# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdither.h

This header declares DeviceN dithering/halftoning functions implemented in `gxdevndi.c`. It includes `gxfrac.h` and forward-declares `gx_device_halftone`.

`gx_render_device_DeviceN` renders an array of fractional process color values into a `gx_device_color`, possibly using a device halftone and phase. `gx_devn_reduce_colored_halftone` reduces a colored halftone with zero or one varying planes to either a pure color or a binary halftone.

Filesystem relevance: none. It is raster color rendering support.
