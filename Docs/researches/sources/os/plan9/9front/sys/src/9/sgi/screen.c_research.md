# File Research: sources/os/plan9/9front/sys/src/9/sgi/screen.c

Implements SGI Newport graphics support and SGI mouse decoding. It defines Newport, VC2, XMAP9, DCB, drawing-mode, and color-map register constants, maps Newport registers, allocates a 1280x1024 RGBX32 software framebuffer, and flushes dirty rectangles to hardware.

`flushmemscreen` lazily switches the graphics mode, disables ARCS console if needed, initializes software cursor mode, then writes rectangle spans through host register writes. Hardware cursor support exists but is disabled via `SWCURSOR`.

`attachscreen` exposes the `Memdata` to `devdraw`; color and blanking hooks are stubs. `sgimouseputc` decodes the 3-byte SGI mouse protocol and calls `mousetrack`.
