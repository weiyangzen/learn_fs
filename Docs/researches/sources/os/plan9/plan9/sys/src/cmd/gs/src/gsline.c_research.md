# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsline.c

Implements Ghostscript line-parameter operators. Device-independent setters/getters cover line width, cap, join, miter limit, dash pattern, dash adaptation, curve join, and dot length. Device-dependent quality/state controls cover flatness, stroke adjustment, accurate curves, and dot orientation.

Important validation behavior:
- cap/join values are range-checked against `gs_line_cap_max`/`gs_line_join_max`;
- miter limit must be at least 1 and stores a derived `miter_check`;
- dash elements must be non-negative and non-empty patterns must have nonzero total length;
- flatness is clamped to `[0.2, 100]`;
- dot length cannot be negative;
- dot orientation only accepts simple axis-aligned or swapped CTMs.

`gx_set_dash` owns dash pattern memory using the graphics state's allocator, resizing/freeing as needed, and precomputes initial dash index, ink state, and remaining distance from the offset.
