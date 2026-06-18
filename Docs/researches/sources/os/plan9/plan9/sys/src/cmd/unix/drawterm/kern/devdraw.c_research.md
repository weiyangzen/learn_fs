# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devdraw.c

Implements the Plan 9 draw device `#i/draw`, mapping draw protocol messages onto drawterm’s host-backed `memdraw` screen.

Key behavior:
- Maintains global draw state in `sdraw`: clients, named images, screen image, flush rectangles, blanking state, and color map backup.
- Exposes top-level `draw`, `new`, per-client directories, and client files `ctl`, `data`, `refresh`, and `colormap`.
- Allocates clients through `new`; each client owns image hash tables, screens, refresh queues, and pending read data.
- Initializes the real screen with `attachscreen` and wraps it as a `Memimage`.
- Implements image install/uninstall, named image management, screen/window allocation, reference counting, and refresh notifications.
- Parses packed draw messages for image allocation, screen allocation, draw, line, polygon, ellipse, font, string, readimage, writeimage, window ordering, clip/repl, named images, and flush.
- Batches screen flushing with rectangle coalescing through `addflush`, `dstflush`, and `drawflush`.
- Provides colormap read/write and default 8-bit colormap loading.

Important interfaces:
- `drawmesg` is the protocol command dispatcher.
- `drawread` returns control info, colormap text, pending image data, or refresh rectangles.
- `drawwrite` handles control IDs, colormap updates, and draw protocol data.
- `drawdevtab` registers device character `i`.

Notable risks:
- This is stateful and relies heavily on correct reference counts for images, named-image aliases, and screens.
- `drawhasclients` intentionally prevents framebuffer resize after any draw client has ever existed.
- Debug printing is mostly disabled by constant conditions in `printmesg`.
