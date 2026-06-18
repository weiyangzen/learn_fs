# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtrac.c

## Purpose
Diagnostic Ghostscript tracing devices that print drawing operations rather than rendering them. It provides sample high-level device implementations for monochrome, RGB, and CMYK tracing.

## Main Concepts
- Devices: `tr_mono`, `tr_rgb`, and `tr_cmyk`.
- Implements low-level callbacks for rectangles, mono/color/alpha copy, masks, tiles, and shape fills.
- Implements high-level path, image, and text tracing.
- Uses Ghostscript debug output macros such as `dprintf`/`dputs`.

## Key Functions
- `trace_drawing_color`, `trace_lop`, `trace_path`, `trace_clip`: formatting helpers for colors, logical ops, paths, and clipping.
- Low-level trace callbacks: `trace_fill_rectangle`, `trace_copy_mono`, `trace_copy_color`, `trace_copy_alpha`, `trace_fill_mask`, shape/tile callbacks.
- `trace_fill_path`, `trace_stroke_path`: dump path contents and state.
- `trace_begin_typed_image`, `trace_plane_data`, `trace_end_image`: trace image setup and incoming image planes.
- `trace_text_begin`: dumps text operation flags, font name, text/glyph data, width adjustments, and optionally creates a text enumerator for supported cases.

## Dependencies
Uses Ghostscript core device, path, clip path, color, image, font, text, and imager-state internals.

## Notable Risks
- Designed for diagnostics, not production rendering; many operations return success without drawing.
- Several callbacks print placeholders such as `**fill_trapezoid**` or default to generic handling.
- Text width handling is explicitly marked wrong for Type 0 fonts.
- Debug output can expose document text and drawing details.

## Filesystem Relevance
No filesystem logic. Output is diagnostic logging through Ghostscript debug facilities.
