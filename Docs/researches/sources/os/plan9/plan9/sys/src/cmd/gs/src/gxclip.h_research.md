# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclip.h

## Purpose
Defines shared internal callback state for clipping devices and declares rectangle-processing callback procedures used by rectangle-list and mask clipping implementations.

## Main Responsibilities
- Defines `clip_callback_data_t`, a common closure object for clipped span callbacks.
- Declares callback functions implemented in `gxclip.c`.
- Provides a shared ABI between rectangle clipping and mask clipping paths.

## Key Structures
`clip_callback_data_t` stores:
- Target device pointer.
- Original operation rectangle.
- Bitmap source data, raster, and source X offset.
- Color or drawing-color payloads.
- Alpha depth and logical operation.
- Tile/texture state and phase values.
- Strip-copy RasterOp color arrays.

## Dependencies
- Requires Ghostscript core types such as `gx_device`, `gx_color_index`, `gx_drawing_color`, `gx_clip_path`, and `gx_strip_bitmap`.

## Research Notes
This header intentionally uses one broad callback structure instead of operation-specific structures. That reduces boilerplate but means each callback must know which fields are valid for its operation.
