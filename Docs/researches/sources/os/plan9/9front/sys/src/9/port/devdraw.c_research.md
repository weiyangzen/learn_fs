# File Research: sources/os/plan9/9front/sys/src/9/port/devdraw.c

Purpose: draw device `#i`, implementing Plan 9 draw protocol client management, image/screen/window objects, refresh delivery, colormap access, and drawing message execution.

Exposed interface: top-level `draw`, `winname`, `new`; each client directory exposes `colormap`, `ctl`, `data`, and `refresh`. Opening `new` allocates a client and returns its `ctl`.

Core implementation: global `sdraw` tracks clients and named images under `drawlock`. `Client` holds image hash buckets, screen refs, refresh queue, read buffer, busy flag, operation state, and ids. `DImage`, `DScreen`, `CScreen`, and `DName` manage Memimage/Memscreen ownership, reference counts, names, windows, and public screen sharing.

Drawing protocol: `drawmesg` parses binary commands such as allocate image/screen, draw, affine warp, ellipse, line, polygon, text, read image, write image, name/attach image, move/top/bottom windows, set operator, and visible/flush. It calls memdraw/memlayer primitives and records flush rectangles for screen updates.

Lifecycle: `drawopen` initializes screen image and installs id 0 from the named screen image for a new client. `drawclose` decrements client refs, frees refresh records, screens, names, images, and client slots when last Chan closes. `drawread` returns client ids, image data, refresh messages, colormap data, and winname. `drawwrite` handles colormap writes and draw protocol data.

Dependencies: `draw.h`, `memdraw.h`, `memlayer.h`, cursor/screen interfaces, and framebuffer attach/flush hooks.

Research notes: this is a large binary protocol interpreter. Review should focus on length checks in each command, image/screen refcount balance, named-image invalidation, refresh queue wakeups, and operations that temporarily alter clip rectangles or allocate variable-size point arrays.
