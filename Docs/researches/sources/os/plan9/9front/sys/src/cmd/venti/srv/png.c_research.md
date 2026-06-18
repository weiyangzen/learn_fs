# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/png.c

`png.c` writes `Memimage` data as PNG over an `Hio` HTTP stream. It emits PNG signature, `IHDR`, deflated `IDAT` chunks, CRCs, and `IEND`.

The encoder converts images to RGB or RGBA memory format, translates Plan 9 premultiplied alpha to non-premultiplied PNG alpha, and feeds scanlines with filter type 0 into `deflatezlib()`. Static initialization sets up flate and CRC tables once under a lock.

This supports Venti’s web graph rendering path. The implementation is minimal and write-only: no PNG parsing, filtering choices, or palette handling.
