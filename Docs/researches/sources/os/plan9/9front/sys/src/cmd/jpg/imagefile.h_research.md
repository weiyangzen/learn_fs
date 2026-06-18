# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/imagefile.h

This is the shared interface header for Plan 9 image codec frontends and writers.

Key contents:
- Defines `Rawimage`, including rectangle, colormap, channel array, channel descriptor, channel length, and GIF metadata.
- Defines channel descriptor enum values for RGB, YCbCr, luminance, RGBV, packed RGB/RGBA, and alpha variants.
- Defines GIF and PNG metadata flags plus `ImageInfo`.
- Declares decoders for JPG/PNG/TIFF/GIF/pixmap, conversion helpers, raw image writer, GIF/PPM/JPG/PNG/TIFF writers, and one/multi-channel conversion helpers.

Research notes:
- This header is the local contract linking the frontend commands to format-specific read/write implementation files elsewhere in the `jpg` directory.
