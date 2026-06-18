# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/rlist.c

Rectangle-list union and simplification utility for VNC update regions.

Key responsibilities:
- Grows and frees dynamic rectangle lists.
- Adds rectangles while merging adjacent/aligned rectangles and eliminating covered rectangles.
- Splits overlapping rectangles using edge, corner, and stride subtraction helpers.
- Maintains a bounding box and optional verbose diagnostics.
- Includes a `REGION_DEBUG` standalone test harness.

Important behavior:
- `addtorlist()` starts with the new rectangle in a temporary list, then iteratively intersects existing rectangles and may add split leftovers back to the temporary queue.
- Aborts on unhandled overlap decomposition.
- Global `tot` limits total allocated rectangles and fatally stops above 10000.

Risks:
- Region algorithm is handcrafted and sensitive to rectangle edge cases.
- Uses global accounting across all lists.
