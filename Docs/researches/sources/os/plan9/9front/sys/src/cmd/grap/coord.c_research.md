# File Research: sources/os/plan9/9front/sys/src/cmd/grap/coord.c

Coordinate-system state for `grap`. It tracks default/current coordinate names, explicit x/y ranges, log-axis flags, and whether explicit coordinates suppress margins.

`coord_x`, `coord_y`, and `coordlog` collect pending parser state; `coord` applies it to an `Obj`, validates log lower bounds, handles implicit default-coordinate renaming after repeated default definitions, and disables automatic x indexing. `resetcoord` switches the current coordinate system.
