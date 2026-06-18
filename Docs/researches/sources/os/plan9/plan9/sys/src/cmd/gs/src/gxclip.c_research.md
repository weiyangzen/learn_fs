# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclip.c

## Purpose
Implements Ghostscript’s rectangle-list clipping device. It wraps a target `gx_device` and intercepts drawing operations, forwarding only the portions that intersect the current `gx_clip_list`.

## Main Responsibilities
- Defines the `"clipper"` device descriptor `gs_clip_device`.
- Builds clipping devices via `gx_make_clip_translate_device` and `gx_make_clip_path_device`.
- Enumerates intersections between requested drawing rectangles and a sorted list of clip rectangles.
- Forwards clipped fragments to target device procedures for:
  - `fill_rectangle`
  - `copy_mono`
  - `copy_color`
  - `copy_alpha`
  - `fill_mask`
  - `strip_tile_rectangle`
  - `strip_copy_rop`
- Implements clipping-box calculation and translated `get_bits_rectangle`.

## Key Implementation Details
- `clip_enumerate` translates client coordinates by `rdev->translation` before clipping.
- `clip_enumerate_rest` keeps a mutable cursor `rdev->current` into the clip list for locality.
- Fast paths avoid full enumeration when the operation lies inside the current clip rectangle.
- `CHECK_VERTICAL_CLIPPING` enables lookahead to coalesce vertically adjacent full-width spans.
- Multi-rectangle operations use shared callbacks declared in `gxclip.h`.

## Important Data Flow
Input drawing op -> translate coordinates -> test current clip rect -> enumerate intersecting spans -> callback forwards span to target device.

## Notable Edge Cases
- Zero or negative width/height returns success without forwarding.
- Single-rectangle clip lists are optimized separately from list-head/list-tail dummy structures.
- `fill_mask` delegates to `gx_default_fill_mask` when an additional `pcpath` is supplied.
- `clip_get_clipping_box` caches the computed box and reverses translation for client coordinates.

## Dependencies
- `gxclip.h` for callback payloads and callbacks.
- `gxcpath.h` / `gxpath.h` for clip path/list conversion.
- Target device procedure table for all forwarded drawing operations.

## Research Notes
This is a core clipping adapter: it does not render itself, but slices drawing calls into clipped target calls. The correctness of coordinate translation and `rdev->current` cursor maintenance is central to avoiding missed or duplicated drawing spans.
