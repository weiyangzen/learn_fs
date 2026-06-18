# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gspaint.c

Implements core Ghostscript painting operations: erase page, fill page, fill/eofill, stroke, and strokepath. It bridges graphics-state color/path state to device-level fill and stroke routines.

Main behavior:
- `gs_erasepage` saves state, sets gray to white, fills the full page, then restores state.
- `gs_fillpage` bypasses clipping and fills the whole device using high-level color if available, otherwise `gx_fill_rectangle`.
- `fill_with_rule`, `gs_fill`, and `gs_eofill` render current paths with winding or even/odd fill rules.
- `gs_stroke` handles charpath merging, null devices, alpha buffering, dash scaling, flatness scaling, and stroke-to-fill conversion when antialias buffering is needed.
- `gs_strokepath` replaces the current path with its stroked outline.

Important internals:
- Alpha-buffer setup scales path and clipping state with `scale_paths`.
- Dash patterns are scaled for antialias buffers and restored afterward.
- Null-device special cases avoid unnecessary color loading.

Dependencies are graphics state, path, clipping path, device color, memory devices, and low-level paint routines.
