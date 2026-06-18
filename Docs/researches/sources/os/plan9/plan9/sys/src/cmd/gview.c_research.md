# File Research: sources/os/plan9/plan9/sys/src/cmd/gview.c

Interactive Plan 9 graphical viewer/editor for polygonal line graphs.

- Input format: one `x y` point per line, followed by a label line per polyline. Multiple input files or stdin can be loaded.
- Maintains linked-list `fpolygon` objects inside global `univ`, with bounding boxes, display rectangle, slant height, current color/thickness, and optional multi-color schemes parsed from labels.
- Implements coordinate transforms from floating-point data coordinates to screen coordinates, including zoom, zoom-out, square-up, recenter, and slant display.
- Draws axes, tick marks, scaled labels, top range text, clipped polylines, selected-point marker, and optional dot-only plotting.
- Provides selection by mouse proximity, logs selected coordinates and optionally labels, and supports interactive recolor, thicken/thin, delete, undo, restack, read, write, move, and rotate.
- Uses Plan 9 graphics/event APIs: `<draw.h>`, `<event.h>`, `emouse`, `ekbd`, `emenuhit`, `egetrect`, and `initdraw`.

Important data structures: `fpoint`, `frectangle`, `fpolygon`, `fpolygons`, `transform`, `thick_color`, `pt_on_fpoly`, and undo record `e_action`.

Notable concerns:
- Movement and rotation are disabled by default unless `-m` is supplied.
- Several allocations are unchecked or only partially checked, consistent with older C style.
- Input parsing is intentionally simple and treats malformed label/point sequences as syntax errors.
- Output rewrites labels to reflect current color/thickness.
