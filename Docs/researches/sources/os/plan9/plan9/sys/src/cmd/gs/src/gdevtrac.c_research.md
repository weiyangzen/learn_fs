# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtrac.c

Implements diagnostic Ghostscript tracing devices that print low-level and selected high-level drawing operations instead of rendering output.

Key behavior:
- Provides internal printers for `gx_drawing_color`, logical operation values, paths, and nontrivial clipping paths.
- Low-level procedures log `fill_rectangle`, `copy_mono`, `copy_color`, `copy_alpha`, `fill_mask`, parallelogram/triangle fills, thin lines, strip tile rectangles, and placeholder messages for unsupported paths such as trapezoid and ROP tracing.
- High-level `trace_fill_path` and `trace_stroke_path` print path segments, drawing color, fill/stroke parameters, and clip information.
- Defines a minimal `trace_image_enum_t` image enumerator that logs plane data calls, tracks rows remaining, and frees itself at image end.
- `trace_begin_typed_image` logs image type and image matrix, handles image types 1/3/4 enough to compute component/plane metadata, returns immediately for type 2 images with no data, and otherwise falls back to Ghostscript’s default typed-image handling.
- `trace_text_begin` logs text operation flags, font name, text/glyph data, widths/deltas, and drawing color; for simple width-return cases it can compute total width and update the current path, otherwise it falls back to the default text path.
- Defines three concrete devices: `tr_mono` (1-bit monochrome), `tr_rgb` (24-bit RGB), and `tr_cmyk` (4-bit CMYK).

Dependencies:
- Uses Ghostscript graphics, path, clipping, image, font, text, imager-state, halftone, and device headers.
- Relies on Ghostscript debug output macros (`dputs`, `dprintf*`) and default fallback device procedures.

Research notes:
- This is a debugging/instrumentation device and intentionally leaves many operations as logged no-ops or default fallbacks.
- Text width computation is explicitly marked as copied from `pdfwrite` and wrong for Type 0 fonts.
