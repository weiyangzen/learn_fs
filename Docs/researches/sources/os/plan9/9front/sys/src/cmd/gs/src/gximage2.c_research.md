# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gximage2.c

Ghostscript ImageType 2 implementation, which copies pixels from an existing graphics state/device region rather than consuming explicit source data.

Key behavior:
- Defines `gs_image_type_2` with custom source-size and begin-image procedures, and no stream serialization support.
- `image2_set_data` transforms the source rectangle from the source graphics state into device bounds and synthesizes an ImageType 1-style image descriptor.
- `gx_image2_source_size` reports the computed source width/height.
- `gx_begin_image2` validates PixelCopy compatibility, computes source and destination matrices, allocates a row buffer, and then either direct-copies pixels or re-emits them through the normal typed image pipeline.
- Supports optional `UnpaintedPath` population using unread rectangles reported by `get_bits_rectangle`.
- Handles RGB/alpha conversion for non-PixelCopy mode and direct native-color copying for simple PixelCopy cases.

Notable dependencies:
- Graphics state and device APIs: `gscoord.h`, `gsdevice.h`, `gxgetbit.h`, `gxpath.h`.
- Image type definitions from `gsiparm2.h` and `gxiparam.h`.

Research notes:
- The file contains explicit limitations: PixelCopy depth handling is incomplete, only simple cases are supported, and one Y computation is marked as rounded/wrong.
- On success, `gx_begin_image2` performs all rendering immediately and returns `1` because ImageType 2 has no caller-supplied data stream.
