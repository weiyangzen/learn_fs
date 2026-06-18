# File Research: sources/os/plan9/9front/sys/src/cmd/gview.c

Implements `gview`, an interactive graphical viewer/editor for labeled 2D polygonal line graphs.

Key points:
- Reads ASCII input containing one `x y` point per line, with a label terminating each polyline.
- Maintains a linked list of `fpolygon` objects under global `fpolygons univ`.
- Computes floating-point bounding boxes, display windows, transforms, slanted views, zoom-in/zoom-out regions, recentering, and square aspect adjustment.
- Draws a Plan 9 window using `draw` and `event`, including frame, axis ticks, numeric labels, unit scaling text, colors, and selected-point markers.
- Supports label-driven colors and thickness:
  - explicit names such as `Red`, `Blue`, `Dkgreen`
  - `Thick`
  - `Multi(...)` schemes selectable by key
- Provides clipping against the visible parallelogram before drawing or selecting paths.
- Selection logic finds the nearest point or path segment within a tolerance rectangle after applying the active slant transform.
- Editing features include recolor, thicken/thin, delete, undo, move, rotate, restack, read more data, and write data.
- Optional `-l` logs selected coordinates and labels; `-m` enables movement/rotation; `-p` plots vertices as dots.
- Uses Plan 9 mouse buttons:
  - button 1 selects and optionally drags
  - button 2 opens edit menu
  - button 3 opens main menu

Dependencies and interactions:
- Uses Plan 9 `<draw.h>`, `<event.h>`, and `<cursor.h>`, plus libc and stdio.
- No filesystem implementation dependency, but it reads and writes local graph data files.
- State is largely global and event-driven.

Research relevance:
- A self-contained interactive command that demonstrates Plan 9 graphical UI patterns, event handling, text prompting, geometry transforms, and file-backed editing.
