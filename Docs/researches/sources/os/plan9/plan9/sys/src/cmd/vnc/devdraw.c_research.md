# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/devdraw.c

Large user-space implementation of Plan 9’s `draw` device over a memory framebuffer used by VNC.

Key responsibilities:
- Exposes `#i/draw`, `new`, per-client directories, `ctl`, `data`, `colormap`, and `refresh`.
- Manages draw clients, image IDs, named images, screens, windows/layers, refresh messages, and reference counts.
- Attaches the VNC framebuffer as image id 0 through `attachscreen()`.
- Parses binary draw protocol messages on `data`.
- Implements image allocation/free, screen allocation/free, named image sharing, repl/clip changes, drawing, lines, ellipses/arcs, polygons, strings/fonts, image read/write, window origin changes, stacking, flush, and compositing op selection.
- Tracks dirty framebuffer rectangles and calls `flushmemscreen()` for VNC update propagation.
- Implements colormap read/write and screen blank/unblank support.

Important behavior:
- Qid path packs file type plus client slot.
- Image reference counts include opens, screens, fills, and named-image derivations.
- Refresh callbacks queue rectangles for clients using `Refmesg`.
- `drawmesg()` validates message lengths and geometry before dispatching memdraw operations.
- Once any draw client has existed, resizing is considered unsupported.

Risks:
- This file is highly stateful and lock-dependent around `sdraw`.
- Binary protocol parsing is manual; bad lengths or IDs produce Plan 9 errors.
- Some comments mark incomplete cleanup/detach and inefficient flush behavior.
