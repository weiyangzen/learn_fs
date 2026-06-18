# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/rows.c

Top-level row and column layout management for Abaco.

Key responsibilities:
- Initializes the row tag and column array.
- Adds columns at a given x position and redistributes available width.
- Resizes all columns when the row rectangle changes.
- Supports dragging column boundaries.
- Closes columns and compacts the column array.
- Hit-tests points against row tag or columns.

Dependencies:
- Uses `Column`, `Row`, `Text`, drawing APIs, and column functions from `cols.c`.

Notable risks:
- Geometry is manually redistributed; small widths and edge cases are guarded but remain layout-sensitive.
