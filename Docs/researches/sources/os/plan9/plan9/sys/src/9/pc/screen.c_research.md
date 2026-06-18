# File Research: sources/os/plan9/plan9/sys/src/9/pc/screen.c

Generic PC screen/VGA framebuffer, palette, acceleration hook, linear framebuffer, blanking, and software cursor implementation.

Key elements:
- Global screen state: `gscreen`, `gscreendata`, `vgascreen[0]`, default arrow cursor, physical screen rectangle.
- `screensize` initializes or reallocates the memory image backing the screen, choosing soft screen memory or mapped framebuffer, then clears and flushes it.
- `screenaperture` allocates/maps a physical aperture with `upaalloc`/`vmap` when a driver lacks a preconfigured linear region.
- `attachscreen` exposes framebuffer metadata to draw clients.
- `flushmemscreen` copies soft-screen updates to paged VGA memory or delegates to driver flush.
- `getcolor`, `setpalette`, `setcolor` manage DAC palette state.
- `cursoron`, `cursoroff`, `setcursor` delegate to the active cursor implementation.
- `hwdraw` dispatches simple fill/scroll operations to VGA driver acceleration hooks while avoiding software cursor artifacts.
- `blankscreen` delegates blanking to driver or generic VGA blank.
- `vgalinearpciid`, `vgalinearpci`, `vgalinearaddr` locate/map linear PCI framebuffers and request write-combining MTRR.
- Software cursor path maintains backing store and cursor images; `swcursorclock` refreshes cursor on timer.

Interactions:
- Uses PCI helpers for video BAR discovery.
- Uses `vmap`, `upaalloc`, and `mtrr`.
- Interfaces with draw/memdraw and device-specific VGA drivers through `VGAdev`/`VGAcur`.

Research notes:
- Graphics subsystem support; not filesystem-specific.
- Framebuffer mapping behavior depends on low-level memory/MMU/PCI code in this same group.
