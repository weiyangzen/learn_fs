# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/slider.c

Implements a simple horizontal or vertical slider widget.

Key behavior:
- Orientation is chosen by comparing requested width and height.
- Draws filled slider range from zero to current value.
- Mouse drag updates `val`, redraws, and invokes callback with button mask, value, and range.
- `plsetslider()` sets value programmatically in screen coordinates from logical value/range.

Important dependencies: `pl_sliderupd`, draw/layout helpers.

Notable risks:
- `plsetslider()` divides by `range`; callers must avoid zero range.
