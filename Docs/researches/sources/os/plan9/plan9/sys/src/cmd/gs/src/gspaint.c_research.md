# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gspaint.c

Implements Ghostscript library painting operations: erase page, fill page, path fill, even-odd fill, stroke, and strokepath.

Key functions:
- `gs_erasepage`: saves state, sets gray to white, calls `gs_fillpage`, restores state.
- `gs_fillpage`: fills the full device using high-level color if available, otherwise `gx_fill_rectangle`, temporarily resetting RasterOp.
- `alpha_buffer_bits`, `alpha_buffer_init`, `alpha_buffer_release`: anti-alias buffer setup for fill/stroke paths.
- `scale_paths`, `scale_dash_pattern`: adjust current path, clipping paths, view clip, effective clip, and dash parameters for alpha-buffer supersampling.
- `fill_with_rule`, `gs_fill`, `gs_eofill`: load device color, optionally alpha-buffer, call `gx_fill_path`, then `gs_newpath`.
- `gs_stroke`: handles charpath merging, null-device fast path, alpha-buffered stroke conversion, or direct `gx_stroke_fill`.
- `gs_strokepath`: replaces current path with stroked outline via `gx_stroke_add`.

Integration:
- Uses path, clipping, device, high-level color, memory-device, and graphics-state internals (`gzstate.h`, `gzpath.h`, `gzcpath.h`, `gxpaint.h`, `gxdevmem.h`).
- Alpha buffering relies on device `get_alpha_bits` and memory alpha-buffer devices.

Risk notes:
- Alpha-buffer scaling must preserve aliasing among `path`, `clip_path`, `view_clip`, and `effective_clip_path`; errors here can corrupt clipping.
- Stroke alpha-buffer path temporarily mutates line width, dash pattern, and flatness and must restore them exactly.
