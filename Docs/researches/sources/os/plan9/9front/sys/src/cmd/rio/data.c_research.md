# File Research: sources/os/plan9/9front/sys/src/cmd/rio/data.c

Static visual data and color initialization for `rio`. Defines cursor bitmaps for crosshair, box, sight, arrow, query, resize corners/edges, and skull.

`iconinit()` allocates background and UI color images, including reverse-video variants and hold/selection/title colors.

No event logic lives here; it is shared visual state for the window manager.
