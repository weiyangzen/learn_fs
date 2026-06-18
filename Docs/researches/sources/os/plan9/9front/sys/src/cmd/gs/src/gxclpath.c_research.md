# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclpath.c

Implements high-level path and graphics-state command writing for Ghostscript command lists. It serializes fills, strokes, polygon fills, clip paths, drawing colors, and compact path segments into per-band command streams.

Key behavior:
- Computes colors-used summaries for pure colors, binary halftones, colored halftones, and unknown/complex drawing colors.
- `cmd_slow_rop` determines whether a RasterOp requires slow full-pixel handling, simplifying the ROP when a pure texture color is known black or white.
- `cmd_put_drawing_color` serializes device colors into extended clist commands, inserting a changed halftone first and updating tile phase when required.
- `cmd_clear_known` clears selected known-state bits across all bands when a cached graphics-state value changes.
- `cmd_check_clip_path` tracks the current clip path pointer and ID, marking clip state dirty when the ID changes.
- `cmd_check_fill_known` compares fill-relevant imager-state fields and accumulates which values must be re-emitted per band.
- Serializes CTM values through Ghostscript stream matrix encoding.
- `cmd_write_unknown` emits missing per-band graphics-state parameters: cap/join, curve/stroke flags, flatness, line width, miter limit, overprint/blend/text knockout, opacity/shape alpha, alpha, fill adjust, CTM, dash pattern, clip path, and color space.
- Clip serialization writes begin/end clip commands and encodes rectangular clips as fill rectangles, path clips as compact path commands, clip-list clips as rectangles, or outer-box fallback when complex clips are disabled.
- `clist_fill_path` computes affected bands from the path bounding box, updates graphics state/color/ROP/clip per band, and serializes the fill path; it falls back to default rendering when clist fill path is disabled or color serialization fails.
- `clist_stroke_path` computes stroke expansion, handles dash pattern limits, updates stroke-specific state, and serializes the stroke path; long dash patterns or disabled path banding fall back to default rendering.
- `clist_fill_parallelogram` uses the rectangle fast path for axis-aligned rectangles and otherwise converts the shape to a polygon path.
- `clist_fill_triangle` similarly converts the triangle to a temporary polygon path.
- `cmd_put_segment` writes compact relative path segment commands, shortening horizontal/vertical lines, merging consecutive lines, and selecting short encodings for fixed-point deltas.
- Curve encoding recognizes common curve shapes and previous-curve symmetry to use specialized compact opcodes.
- `cmd_put_path` enumerates a `gx_path`, skips segments entirely outside the current band Y range when safe, emits catch-up moveto/lineto segments when crossing back into range, handles implicit closepath, preserves requested segment notes, and finally writes the path operation.

Dependencies:
- Uses command-list device/path definitions from `gxcldev.h` and `gxclpath.h`, Ghostscript paths from `gzpath.h`, clip paths from `gzcpath.h`, device colors from `gxdcolor.h`, paint parameters from `gxpaint.h`, and stream serialization from `stream.h`/`gsserial.h`.
- Calls lower-level command buffer helpers such as `set_cmd_put_op`, `cmd_write_rect_cmd`, `cmd_update_lop`, `cmd_set_tile_phase`, and `cmd_put_halftone`.

Research notes:
- Per-band known-state flags are the main compression mechanism for graphics state; every state change must clear the appropriate flags before new commands are emitted.
- Path serialization is band-aware for fills and undashed strokes, but dashed strokes cannot skip out-of-band segments because doing so would corrupt dash phase.
- The fallback paths are important compatibility escapes for disabled clist features, overly long dash patterns, and unsupported drawing color serialization.
