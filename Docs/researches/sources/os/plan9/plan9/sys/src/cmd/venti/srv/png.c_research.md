# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/png.c

Purpose: Writes Plan 9 `Memimage` images as PNG streams through the HTTP I/O layer.

Key behavior:
- Emits PNG signature, IHDR, compressed IDAT chunks, and IEND.
- Converts source images to RGB/RGBA channel layouts suitable for PNG.
- Uses zlib deflate callbacks to stream scanlines with filter type 0.
- Converts Plan 9 premultiplied alpha to non-premultiplied alpha for RGBA output.
- Lazily initializes deflate and CRC tables once under a lock.

Dependencies:
- Uses `Memimage`, `Hio`, Plan 9 draw/memdraw locking, flate, and CRC helpers.

Notable details:
- IDAT chunks are capped at 20,000 bytes.
- Only non-interlaced 8-bit RGB/RGBA output is generated.
