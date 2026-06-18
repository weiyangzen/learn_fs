# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/writepng.c

## Purpose
PNG writer for `Memimage`.

## Behavior
Converts input to BGR24 or ABGR32 memory layout so bytes can be written as PNG RGB/RGBA order, writes signature, IHDR, tIME, optional gAMA, optional tEXt comment, deflated IDAT chunks, and IEND.

## Compression
Uses `deflatezlib` with filter type 0 for every scanline. `zread()` injects filter bytes and streams pixels. For alpha, it converts Plan 9 premultiplied alpha back to non-premultiplied RGB before encoding.

## Dependencies
Uses `flate`, CRC helpers, Bio, and memdraw.
