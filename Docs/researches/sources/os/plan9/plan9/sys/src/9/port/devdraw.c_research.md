# File Research: sources/os/plan9/plan9/sys/src/9/port/devdraw.c

Implements `#i/draw`, the in-kernel Plan 9 draw protocol server. It exposes a top-level `draw` directory, `winname`, `new`, per-client directories, and per-client `colormap`, `ctl`, `data`, and `refresh` files.

Core state is in `Draw`, `Client`, `DImage`, `DScreen`, `CScreen`, `DName`, and `Refresh`. `Draw` tracks clients, named images, screen state, blanking state, and saved colormap. `Client` tracks image hash buckets, screens, refresh queue, pending read data, protocol op, and client id. `DImage` wraps `Memimage` with ids, refcounts, font metadata, screen/layer ownership, and optional name inheritance.

Opening `new` allocates a client and returns its `ctl`. Opening `ctl` installs display image id `0` as a named screen image reference. Closing the last client reference frees refresh records, names, screens, images, and flushes the display.

The binary command interpreter in `drawmesg` handles image allocation, screen allocation/use, clipping/repl changes, drawing, ellipses/arcs, lines, polygons, strings/string background, font initialization/loading, named images, window origin/top/bottom ordering, image read/write including compressed writes, freeing resources, and explicit flush. It dispatches to `memdraw`, `memlayer`, and `memimage` primitives.

`drawread` returns image info from `ctl`, colormap text, queued image data from read commands, and refresh rectangles. `drawflush`, `addflush`, and `dstflush` coalesce screen updates before calling `flushmemscreen`.

Screen management includes lazy framebuffer attachment, named screen image creation, screen deletion/reset, default 8-bit colormap setup, screen blanking by hardware plus colormap blackening, and activity/idletime tracking. The implementation is global-lock-heavy through `drawlock` and relies on precise refcounting for images/screens/names.
