# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevxini.c

X11 driver initialization, parameter handling, buffering setup, font mapping, and cleanup.

Key responsibilities:
- `gdev_x_open` opens the X display, handles Ghostview and explicit `WindowID`, selects visual/colormap, reads Xt resources, reserves foreground/background, sets up colors and font maps, creates or adopts a window, builds GC state, clears the window, and initializes Ghostview atoms/window if needed.
- Handles Ghostview geometry/orientation properties and computes the initial matrix/imaging bbox.
- Uses Xt resource tables from `gdevxres.c` for defaults such as palette, font resources, backing pixmap, XPutImage/XSetTile flags, and resolution.
- `x_set_buffer` optionally allocates a memory device buffer up to `MaxBitmap`, forwards drawing through bbox/memory when buffered, and switches device procs accordingly.
- `gdev_x_clear_window` allocates/frees backing pixmap, initializes destination, clears background, and resets color tracking.
- Font map parsing builds `x11fontmap` linked lists from resource strings.
- `gdev_x_finish_copydevice` clears pointer fields after `copydevice` to avoid dangling X/font/buffer references.
- `gdev_x_get_params` / `gdev_x_put_params` expose `WindowID`, `.IsPageDevice`, `MaxBitmap`, and buffered update limits; put-params can resize an open non-Ghostview window.
- `gdev_x_close` sends Ghostview DONE, frees visual info/colors/font maps/colormap, and closes the display.

Notable implementation details:
- X error handling for backing pixmap allocation and `XFreeColors` uses static globals due to Xlib API limitations.
- Default DPI is inferred from screen dimensions when the device still has `FAKE_RES`.
- Closing the Xt resource display is deliberately delayed until after resource-dependent initialization.
- `MaxBitmap` changes can toggle memory-buffered rendering while the device is open.

Filesystem relevance:
- None.
