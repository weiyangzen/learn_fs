# File Research: sources/os/plan9/9front/sys/src/cmd/lens.c

`lens` is an interactive screen magnifier. It opens `/dev/screen`, reads the screen image format and geometry, samples pixels around the current pointer-selected point, magnifies them into its own Draw window, and optionally overlays a grid.

Controls include keyboard zoom/unzoom, numeric magnification, grid toggle, redraw, quit, left mouse to recenter, and right-button menu actions. It supports screen depths of at least 8 bits and uses raw screen buffer reads plus `loadimage()` to render magnified scanlines.

The code is tightly coupled to Plan 9 draw/event APIs and `/dev/screen` layout.
