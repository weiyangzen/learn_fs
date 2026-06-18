# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/data.c

Read status: complete, 180 lines.

This file defines `rio` cursor bitmap data and initializes basic drawing images. It includes crosshair, box, sight, white arrow, query, and edge/corner resize cursors, plus the `corners` table used to pick resize cursors by border region.

`iconinit` allocates the background and red single-pixel images used by the window manager.

Filesystem relevance: no file I/O; supports interactive window management visuals.
