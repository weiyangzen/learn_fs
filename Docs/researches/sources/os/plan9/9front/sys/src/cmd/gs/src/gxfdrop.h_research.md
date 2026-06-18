# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfdrop.h

Defines data structures and interfaces for glyph-fill dropout prevention.

Key definitions:
- `ADJUST_SERIF` and `CHECK_SPOT_CONTIGUITY` enable serif adjustment and local spot-contiguity checks.
- `margin` describes a pixel-index interval to paint.
- `section` stores fractional Y intersections for a half-integer X probe and, when enabled, X coverage bounds.
- `margin_set` groups one half-pixel Y window, its interval list, touched-cache pointer, and section array.
- Debug visualization macros define scale and colors for trapezoids and margins.

Key declarations:
- `init_section`
- `free_all_margins`
- `close_margins`
- `process_h_lists`
- `margin_interior`
- `start_margin_set`
- `continue_margin_common`

Dependencies:
- Forward-declares `active_line` and `line_list`.
- Uses `fixed`, `gx_device`, and Ghostscript GC struct declarations.

Research notes:
- The long header comment is the clearest overview of pseudo-rasterization: two moving `1xN` pixel windows track painted margins and decide whether to add fallback pixels.
- This header is tightly coupled to `gxfill.c` internals rather than a general public API.
