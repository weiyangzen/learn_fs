# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/machdep.c

`machdep.c` is the Plan 9 draw backend for libplot. It manages the offscreen image, display initialization, drawing primitives, text rendering, buffer swaps, double-buffer mode, and cached 1x1 color images.

`m_initialize()` initializes draw, allocates an inset offscreen buffer, sets clipping and mapping rectangles, and centers a square drawing region inside the window. Primitive functions draw to `offscreen` and, unless buffered, mirror to `screen`. `getcolor()` caches allocated solid-color images.
