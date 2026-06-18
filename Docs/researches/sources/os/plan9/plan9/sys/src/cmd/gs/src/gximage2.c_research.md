# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gximage2.c

Ghostscript ImageType 2 implementation, copying pixels from an existing graphics state/device region rather than consuming explicit source data.

Key behavior:
- Defines `gs_image_type_2` with custom source-size and begin procedures, and no stream serialization support.
- `image2_set_data` transforms a source rectangle from the source graphics state into device bounds and synthesizes ImageType 1-style image metadata.
- `gx_image2_source_size` reports the computed source width/height.
- `gx_begin_image2` validates PixelCopy compatibility, computes source/destination matrices, allocates a row buffer, and renders immediately.
- Supports direct native-color copy for simple PixelCopy cases, or re-emits rows through the normal typed-image pipeline for converted RGB/alpha cases.
- Optionally records unread rectangles into `UnpaintedPath` when `get_bits_rectangle` reports gaps.

Notable dependencies:
- Graphics state/device APIs from `gscoord.h`, `gsdevice.h`, and `gxgetbit.h`.
- Path updates via `gxpath.h`.
- ImageType 2 public parameters from `gsiparm2.h`.

Research notes:
- Comments document limitations: PixelCopy depth handling is incomplete, only simple cases are supported, and one Y computation is marked rounded/wrong.
- On success it returns `1` because ImageType 2 has no later caller-supplied data stream.
